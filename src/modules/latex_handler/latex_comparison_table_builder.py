import re
from pathlib import Path
from typing import List

from tenacity import retry, stop_after_attempt, wait_fixed

from src.configs.config import ADVANCED_CHATAGENT_MODEL, BASE_DIR
from src.configs.logger import get_logger
from src.models.LLM import ChatAgent
from src.modules.latex_handler.latex_base_table_builder import LatexBaseTableBuilder
from src.modules.utils import (
    load_file_as_string,
    load_prompt,
    load_single_file,
    save_result,
)

logger = get_logger("src.modules.latex_handler.LatexComparisonTableBuilder")


class LatexComparisonTableBuilder(LatexBaseTableBuilder):
    def __init__(
        self,
        main_body_path: Path,
        tmp_path: Path,
        latex_path: Path,
        outline_path: Path,
        paper_dir: Path,
        prompt_dir: Path,
        chat_agent: ChatAgent,
    ):
        self.chat_agent = chat_agent
        super().__init__(chat_agent=self.chat_agent)
        self.main_body_path = main_body_path
        self.outline_path = outline_path
        self.comparison_table_tex_path = latex_path / "comparison_table.tex"
        self.paper_dir = paper_dir
        self.comparison_prompt_path = prompt_dir / "Comparison.txt"
        self.description_prompt_path = prompt_dir / "Table_description.txt"
        self.rewrite_prompt_path = prompt_dir / "Content_rewrite.txt"
        self.tmp_path = tmp_path
        # self.exist_primary_attribute_path = os.path.join(tmp_path, "exist/Primary Attribute.json")

    def find_method_section(self) -> str:
        outlines = load_single_file(self.outline_path)
        section_titles, subsection_titles = self.parse_outline(outlines)
        ans = None  # 用于保存符合条件的元素
        for section_title in section_titles:
            if (
                "method" in section_title.lower()
                or "technique" in section_title.lower()
            ):
                ans = section_title
                break  # 满足条件，退出循环
        if ans == None:
            prompt = load_prompt(
                f"{BASE_DIR}/resources/LLM/prompts/latex_table_builder/find_method_section.md",
                outline=str(outlines),
            )
            res = self.chat_agent.remote_chat(
                text_content=prompt, model=ADVANCED_CHATAGENT_MODEL
            )
            if res is None:
                return None
            try:
                ans = re.search(r"<Answer>(.*?)</Answer>", res, re.DOTALL)
                if ans:
                    ans = ans.group(1)
                else:
                    print("Error: No <Answer> tag found in the input text.")
                    return
            except Exception as e:
                return
        title = ans
        logger.debug(f"Select method section '{title}' to generate comparison_table.")
        return title

    def generate_comparison_table(self, section_name):
        section_content = self.extract_section_content(
            self.main_body_path, section_name
        )
        if section_content is None:
            return
        prompt = load_prompt(self.comparison_prompt_path, Input=section_content)
        result = self.chat_agent.remote_chat(
            text_content=prompt, model=ADVANCED_CHATAGENT_MODEL
        )
        result = self.extract_and_convert(result)
        if result is None:
            return
        latex_code = self.generate_comparison_table_latex(result)
        caption, introductory_sentence = self.generate_description(
            latex_code, section_content
        )
        caption = re.sub(r"\{[^}]*\}", "", caption)
        caption = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})?", "", caption)
        if caption is not None and introductory_sentence is not None:
            try:
                latex_code = re.sub(
                    r"\\caption\{.*?\}", rf"\\caption{{{caption}}}", latex_code
                )
            except re.error as e:
                print(f"Error during regex substitution for latex_code: {e}")
                return
            try:
                introductory_sentence = re.sub(
                    r"\\?input\{.*?\}",
                    rf"\\ref{{tab:comparison_table}}",
                    introductory_sentence,
                )
            except re.error as e:
                print(f"Error during regex substitution for introductory_sentence: {e}")
                return
            tex = load_file_as_string(self.main_body_path)
            section_mainbody = self.extract_section_mainbody(
                self.main_body_path, section_name
            )
            if section_mainbody == "":
                return
            prompt = load_prompt(
                self.rewrite_prompt_path,
                Content=section_mainbody,
                Sentence=introductory_sentence,
            )
            res = self.chat_agent.remote_chat(
                text_content=prompt, model=ADVANCED_CHATAGENT_MODEL
            )
            # Add introductory sentence
            try:
                revised_content = re.search(r"<Answer>(.*?)</Answer>", res, re.DOTALL)
                if revised_content:
                    revised_content = revised_content.group(1)
                else:
                    print("Error: No <Answer> tag found in the input text.")
                    return
            except Exception as e:
                return
            if "\input{summary_table}" in section_mainbody:
                cleaned_content = revised_content.replace(
                    "\\input{summary_table}", ""
                ).strip()
                replacement_block = "\\input{summary_table}"
                if cleaned_content:
                    replacement_block = (
                        f"{replacement_block}\n{cleaned_content}"
                    )
                tex = tex.replace(section_mainbody, replacement_block)
            else:
                tex = tex.replace(section_mainbody, revised_content)
            save_result(tex, self.main_body_path)
            # Add input\{comparison_table}
            tex = load_file_as_string(self.main_body_path)
            section_content = self.extract_section_content(
                self.main_body_path, section_name
            )
            tex = tex.replace(
                section_content, f"{section_content}\n\n\\input{{comparison_table}}"
            )
            save_result(tex, self.main_body_path)
            self.save_table_file(latex_code, self.comparison_table_tex_path)
            logger.info(
                f"Comparison LaTeX table saved to {self.comparison_table_tex_path}"
            )

    def generate_comparison_table_latex(self, data):
        # 提取公共属性和方法
        common_attributes = data["common_attributes"]
        methods = data["methods"]
        methods = dict(list(methods.items())[:3])

        # LaTeX 表格头部
        latex_code = "\\begin{table}[ht]\n\\centering\n"
        latex_code += "\\resizebox{\\textwidth}{!}{%\n"  # 开始缩放
        latex_code += "\\begin{tabular}{l" + "c" * len(methods) + "}\n\\toprule\n"

        # 填写方法标题行
        method_titles = "\\textbf{{Feature}}"
        for method in methods.keys():
            method_titles += f" & \\textbf{{{method}}}"
        method_titles += " \\\\\n\\midrule\n"
        latex_code += method_titles

        # 填写每个公共属性的行
        for attribute in common_attributes:
            row = f"\\textbf{{{attribute}}}"  # 加粗属性名称
            for method in methods.keys():
                formatted_attribute = self.format_string(
                    methods[method].get(attribute, "N/A")
                )
                row += f" & {formatted_attribute}"

            row += " \\\\\n"
            if self.is_the_row_good(row=row):
                latex_code += row
            else:
                logger.debug(
                    f'Row "{row}" has too many unexpected tokens, it has been removed from comparison table.'
                )

        # 结束表格
        latex_code += "\\bottomrule\n\\end{tabular}}\n\\caption{Comparison of different Methods}\n\\label{tab:comparison_table}\n\\end{table}"
        return latex_code
        # # Save the LaTeX code to a .tex file
        # with open(output_file, "w") as file:
        #     file.write(latex_code)
        # logger.info(f"Comparison LaTeX table saved to {output_file}")

    @staticmethod
    def get_sections(survey_path: str) -> List[str]:
        """
        Get the section names of the survey.
        """
        tex = open(survey_path, "r").read()
        pattern = r"\\section{"
        match_l = list(re.finditer(pattern, tex))
        res = []
        for i in range(len(match_l) - 1):
            section_tex = tex[match_l[i].start() : match_l[i + 1].start()]
            res.append(section_tex)
        return res

    @staticmethod
    def get_title(section: str) -> str:
        """
        Get the title of the section.
        """
        title = re.findall(r"\\section\{([^}]+)\}", section)[0]
        return title

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def run(self):
        method_section = self.find_method_section()
        self.generate_comparison_table(method_section)
