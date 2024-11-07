import logging
import re
from typing import Any, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
import sys
sys.path.append('./')
from file_rag.utils import build_logger


logger = build_logger()


def _split_text_with_regex_from_end(
    text: str, separator: str, keep_separator: bool
) -> List[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
            if len(_splits) % 2 == 1:
                splits += _splits[-1:]
            # splits = [_splits[0]] + splits
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]


class ChineseRecursiveTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(
        self,
        separators: Optional[List[str]] = None,
        keep_separator: bool = True,
        is_separator_regex: bool = True,
        **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or [
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s",
        ]
        self._is_separator_regex = is_separator_regex

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1 :]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = _split_text_with_regex_from_end(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return [
            re.sub(r"\n{2,}", "\n", chunk.strip())
            for chunk in final_chunks
            if chunk.strip() != ""
        ]


if __name__ == "__main__":
    text_splitter = ChineseRecursiveTextSplitter(
        keep_separator=True, is_separator_regex=True, chunk_size=50, chunk_overlap=0
    )
    ls = [
        """
      湖北省数据局文件  省数据局关于开展数据资源开发利用 试点申报的通知  各市、州、直管市、神农架林区数据主管部门:  为贯彻落实党中央、国务院关于数据要素市场化配置改革决 策部署，按照全国数据工作会议及《新时代推动中部地区加快崛 起的若干政策措施》《湖北省数据要素市场建设实施方案》工作 要求，探索我省数据要素市场化配置改革工作路径，加快推动数 据资源整合共享、开发利用和合规流通，拟在全省范围内开展数 据资源开发利用试点。现就相关工作通知如下。  一、试点目标  坚持系统谋划，突出改革创新，鼓励试点地区充分依托我省 已有数据流通利用基础设施, 立足自身数据资源优势和数据应用 场景,围绕数据资源体系建设、数据融合开发、 定价与收益分配、  数据资产登记入表等 7 项试点任务开展积极探索与大胆实践,为 我省深化数据要素市场化配置改革、激发数据要素开发利用活 力、加快数据资源化和资产化进程提供动能。  各地区通过试点工作形成一批协调联动、 推动有力的工作机 制，出合一批操作性强、务实有效的政策措施，在行政事业单位 资产进账入表、数据融合开发、数据空间建设运营、数据产品定 价与收益分配、数据流通激励、行业高质量数据集建设等方面取 得突破.省数据局将根据试点工作情况,建设数据资源开发利用 典型案例库, 形成一批制度创新成果，组织开展经验交流和成果 推广，充分发挥试点的示范引领作用，以试点实践加快推进我省 数据要素市场化配置改革进程。  二、工作任务  数据资源开发利用试点聚焦当前数据资源开发利用的难点、 堵点， 采取“试点任务 + 试点领域” 相结合的方式探索突破路径， 形成可复制可推广的经验做法。  (一) 试点任务。  1 .建立数据资源体系。建立健全数据资源管理制度规范和管 理机制，充分利用已有平台和资源,通过登记管理或其他创新手 段，强化对本地区数据资源梳理和分类分级管理,形成统一目录 和资源体系,增强对各类数据资源引接、汇聚、沧理和开发利用 能力。结合“全套试点”地区大财政体系建设重点工作任务，探 索行政事业单位和国有企业在国有“三资” 管控平台开展数据资  源资产登记; 开展数据资源调查，理清行业高价值数据集分布情 况，建立数据资源“一本账”，促进数据资源登记管理、融合应 用、应和急调度  2.推动数据融合开发。创新公共数据管理和开发利用机制， 探索通过“统一授权+特许开发”模式开展公共数据授权运营， 保证数据安全的前提下促进资源最大化利用。 支持试点地区依托 省级公共数据授权运营平台围绕医疗健康、 交通物流、气象服务、 低空经济、社会信用、卫星迁感、金融风险防控等重点行业领域 打造典型应用场景。 有条件的市州可按全省统一标准统筹建设本 地区授权运营平台,与省级平台对接,形成全省一体化的授权运 营平台体系。 探索建立数据供给激励机制和数据资源开发利用协 同机制，推动融合更大范围的公共数据、社会数据，开发高质量 数据产品和服务。  3.提升技术支撑能力。探索企业、行业、城市和个人可信数 据空间的建设与运营,为跨组织数据融合应用提供数据治理、建 模、测试、产品交付等基础服务，建立可信可控的数据共享流通 环境，解决公共数据授权运营、数据流通交易等过程中不同类型 数据资源提供方、使用方、服务方、监管方等主体间的安全与信 任问题。鼓励企业和科研机构开展身份认证、访问控制、数据加 密、 虹相站报信肖 数据备份、隐私计算等数据可信流通、 安全治理领域技术攻关和产品研发, 推动本地区数据资源开发利 用过程数据链全栈核心环节技术成果转化, 构建自主可控的数据 要素技术支撑体系，  4 探索数据定价与收益分配机制。 鼓励以“补偿成本、适当 获利*的原则将公共数据使用费纳入非税收入管理，建立公共数 据资源定价口径和标准，探索公共数据产品直接成本加成定价、 市场定价、指数定价等定价模式，逐步形成政府指导定价机制; 探索根据数据供给数量和质量等方式评估数据提供单位投入贡 献，以财政部门发放数字化建设专项资金、数据开发利用主体提 供数据和技术反哺服务等多种方式开展收益分配, 建立公共数据 内部收益分配机制及激励机制，保护各方投入的合理收益,激励 数据提供单位持续提供高质量数据资源. 鼓励引入第三方机构进  行课题研究,探索出台相关激励措施，引导企业基于市场规则奸 立企业数据资源价值化和收益分配机制。  5 开展数据流通交易。探索建立数据流通激励机制，鼓励数 据密集型企业、平台型企业等参与数据要素市场化流通工作。 推 动公共数据产品流通交易、政府部门和国有企业数据采购通过省 数据流通交易平台进行. 培育数据要素市场生态，开展数据要素 型企业认定,引导各类市场主体通过省数据流通交易平台开展数 据流通交易等业务,鼓励数据商和第三方专业服务机构提供数据 流通交易相关服务。  6 .推进数据资产登记入表。 引导本地区企业依托省数据产权 登记 (存证 ) 平台与流通交易平台开展数据产权登记、数据资产 评估、安全合规评估等业务，评估计量数据资产价值，开展数据  资产入表。开展数据知识产权登记，推动登记凭证多场景应用。 鼓励商业银行、保险等金融机构创新开展以专利、数据知识产权、 数据资产等为核心资产的质押融资、保险保障等金融服务。  7.建设行业高质量数据集。探索公共数据与社会数据融合、 共建共享高质量数据集的工作机制和政策供给。鼓励科研机构、 行业龙头企业等共建高质量行业共性数据资源库、 行业数据集和 知识库， 覆盖服务大模型研发的预训练集、指令微调数据集和济 试集，形成行业数据采集、存储、清洗、标准化、标注等治理能 力，为行业发展和 AI 大模型训练提供支持.  (二 ) 试点领域。重点围绕城市数字公共基础设施、医汗健 康、交通物流、气象服务、低空经济、社会信用、卫星退感、金 融风险防控、便利支付、自然资源、生态环境保护、绿色低碳、 就业创业、社会保险、文化旅游等领域，打造具有较大经济和社 会效益的典型示范应用场景, 激励更多主体参与数据资源开发利 用。鼓励各地区结合实际拓展其他领域和典型场景。  三、有关要求  请各地区结合本地工作基础和试点意向, 积极开展数据资源 开发利用试点申报,每个试点任务可确定不同试点范围，试点范 围可为本级或者所辖县 (市、区 ) ，认真填写《数据资源开发利 用试点申报表》 ( 见附件 ) ，明确试点目标、试点内容 (含试点 范围 ) 、预期成效、实施路径、进度安排、保障措施等，突出创 新和示范效应。鼓励“一主两副”、“武鄂黄黄”都市轩城市及 其他基础条件较好的地区,结合《新时代推动中部地区加快岂起 的若干政策措施》要求，勇于探索、开拓创新，取得更大试点成 效。  试点任务截至2025 年7 月，2024 年 12 月底将组织中期验 收，重点审查建立数据资源体系、推动数据融合开发、开展数据 流通交易、推进数据资产登记入表等工作进展情况，以落实推动 中部地区加快崛起、大财政体系建设等相关任务要求。  请各单位就相关试点工作报本级人民政府分管领导同意后， 于2024年7月30日17:00 前将加盖本单位公章的申报表〈含 word/WPS 版本 ) 以邮件方式反馈至省数据局数据资源处。  联系人: 陈，款，027-87235703，13212770811  沈江涛，027-87235392，13618664966 邮箱: hbssjjDATAG@163.com  附件: 数据资源开发利用试点申报表  附件  数据资源开发利用试点申报表  AM   口数据资源体系 ”口数据融合开发 口技术支撑能力  口定价与收益分配 口数据资产登记入表      口数据流通交易 口行业高质量数据集建设  口城市数字公共基础设施     口医疗健康  试点领域 (可多选)  口交通物流 口社会信用 口便利支付 口绿色低碳  |口文化旅游  数据资源情 况 (800 字 内 )  (已有数据资源， 范围、数据资源内容及数据项等简要描述，  优势 )  口气象服务 口卫星还感 口自然资源 口就业创业  口低空经济 口金融风险防控 口生态环境保护 口社会保险  口其他《请注明)  况措述，包括数据资源类别、  数据资源 突出行业数据 单位意见  L__ |一一一  省数据局办公室  (已有数据资源开发利用工作机制，包括数据开发利用铀 度体系、管理措施、基础设施平台、人才、技术、资金支 持、已开展的典型做法等 )  (试点目标 (尽可能量化) 、试点内容〔含试点范围) 、 预期成效、实施路径、进度安排、保障措施等 )  (关于数据资源开发利用试点后续工作建议 )  单位盖章 年 月 日  2024年7月18日印发 
        """,
    ]
    # text = """"""
    for inum, text in enumerate(ls):
        print(inum)
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            print(chunk)
