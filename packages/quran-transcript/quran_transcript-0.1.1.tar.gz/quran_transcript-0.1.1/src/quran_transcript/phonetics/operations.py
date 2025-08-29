from dataclasses import dataclass, field
import re

from .conv_base_operation import ConversionOperation
from .moshaf_attributes import MoshafAttributes
from ..alphabet import uthmani as uth
from ..alphabet import phonetics as ph


@dataclass
class DisassembleHrofMoqatta(ConversionOperation):
    arabic_name: str = "فك الحروف المقطعة"
    regs: tuple[str, str] = ("", "")

    def forward(self, text, moshaf):
        for word, rep in uth.hrof_moqtaa_disassemble.items():
            text = re.sub(f"(^|{uth.space}){word}({uth.space}|$)", f"\\1{rep}\\2", text)
        return text


@dataclass
class SpecialCases(ConversionOperation):
    arabic_name: str = "فك الحالات الخاصة"
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [DisassembleHrofMoqatta()]
    )
    regs: tuple[str, str] = ("", "")

    def forward(self, text, moshaf: MoshafAttributes):
        for case in uth.special_patterns:
            pattern = case.pattern
            if case.pos == "start":
                pattern = r"^" + pattern
            elif case.pos == "end":
                pattern = pattern + r"$"

            if case.attr_name is not None:
                moshaf_attr = getattr(moshaf, case.attr_name)
                if moshaf_attr in case.opts:
                    rep_pattern = case.opts[moshaf_attr]
                else:
                    rep_pattern = case.pattern
            elif case.target_pattern is not None:
                rep_pattern = case.target_pattern

            text = re.sub(pattern, rep_pattern, text)

        return text


@dataclass
class BeginWithHamzatWasl(ConversionOperation):
    arabic_name: str = (
        "تحويل همزة الوصل في البداية لهمة في الأسماء والأفعلا والمعرف بأل"
    )
    regs: tuple[str, str] = ("", "")
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            DisassembleHrofMoqatta(),
            SpecialCases(),
        ]
    )

    def _get_verb_third_letter_haraka(self, verb: str):
        if verb in uth.begin_hamzat_wasl.damma_aarida_verbs:
            return uth.kasra

        letters = f"{uth.pure_letters_group}{uth.hamazat_group}"
        match = re.search(
            f"^{uth.hamzat_wasl}(?:{uth.noon}[{uth.noon_ikhfaa_group}]|[{letters}]{uth.shadda}|(?:{uth.noon}{uth.meem_iqlab}|[{letters}][{uth.harakat_group}{uth.ras_haaa}])[{letters}])(.)",
            verb,
        )
        if match:
            haraka = match.group(1)
            if haraka == uth.dama:
                return uth.dama
            elif haraka in {uth.kasra, uth.fatha}:
                return uth.kasra
            else:
                raise ValueError(
                    f"Can no determine haraka exeptected: ضمة أو فتحة أو كسرة got : `{haraka}`"
                )

        raise ValueError("Can not found match to extract harak")

    def forward(self, text: str, moshaf):
        if re.search(f"^{uth.hamzat_wasl}", text):
            words = text.split(uth.space)
            first_word = words[0]
            # الأسماء
            if (first_word in uth.begin_hamzat_wasl.verbs_nouns_inter) or (
                first_word in uth.begin_hamzat_wasl.nouns
            ):
                first_word = re.sub(
                    f"(^){uth.hamzat_wasl}",
                    f"\\1{uth.hamza}{uth.kasra}",
                    first_word,
                )
            # الأفعال
            elif first_word in uth.begin_hamzat_wasl.verbs:
                third_letter_haraka = self._get_verb_third_letter_haraka(first_word)
                first_word = re.sub(
                    f"(^){uth.hamzat_wasl}",
                    f"\\1{uth.hamza}{third_letter_haraka}",
                    first_word,
                )

                # اجتماع همزتان
                haraka_to_letter_madd = {
                    uth.kasra: uth.yaa,
                    uth.dama: uth.waw,
                }
                first_word = re.sub(
                    f"(^{uth.hamza}.)[{uth.hamazat_group}]{uth.ras_haaa}",
                    f"\\1{haraka_to_letter_madd[third_letter_haraka]}",
                    first_word,
                )

            # المعرف بأل
            else:
                first_word = re.sub(
                    f"(^){uth.hamzat_wasl}",
                    f"\\1{uth.hamza}{uth.fatha}",
                    first_word,
                )

            # joing again
            text = uth.space.join([first_word] + words[1:])
        return text


@dataclass
class BeginWithSaken(ConversionOperation):
    arabic_name: str = "البدأ بحرف ساكن"
    regs: tuple[str, str] = (
        f"(^.){uth.ras_haaa}",
        f"\\1{uth.kasra}",
    )


@dataclass
class ConvertAlifMaksora(ConversionOperation):
    arabic_name: str = "تحويل الأف المقصورة إله: حضف أو ألف أو ياء"
    regs: list[tuple[str, str]] = field(
        default_factory=lambda: [
            # حذف الأف المقصورة من الاسم المقصور النكرة
            (
                f"({uth.tanween_fath_modgham}|{uth.tanween_fath_iqlab}|{uth.tanween_fath_mothhar}){uth.alif_maksora}",
                r"\1",
            ),
            # تحويلا الألف المقصورة المحضوفة وصلا إلى ألف
            (
                f"({uth.fatha}){uth.alif_maksora}({uth.space}|$)",
                f"\\1{uth.alif}\\2",
            ),
            # تحويل الألف الخنرجية في السم المقصور لألف
            (
                f"{uth.alif_maksora}{uth.alif_khnjaria}",
                f"{uth.alif}",
            ),
            # تحويلا الألف المقصورة المسبوقة بكسرة إلي ياء
            (
                f"{uth.kasra}{uth.alif_maksora}",
                f"{uth.kasra}{uth.yaa}",
            ),
            # ياء
            (
                f"{uth.alif_maksora}([{uth.harakat_group}{uth.ras_haaa}{uth.shadda}{uth.tanween_dam}{uth.madd}])",
                f"{uth.yaa}\\1",
            ),
        ]
    )


@dataclass
class DeleteShaddaAtBeginning(ConversionOperation):
    arabic_name: str = "حذف الشدة من الحرف الأول"
    regs: tuple[str, str] = (
        f"(^.){uth.shadda}",
        r"\1",
    )


@dataclass
class NormalizeHmazat(ConversionOperation):
    arabic_name: str = "توحيد الهمزات"
    regs: tuple[str, str] = (
        f"[{uth.hamazat_group}]",
        f"{uth.hamza}",
    )


@dataclass
class IthbatYaaYohie(ConversionOperation):
    arabic_name: str = "إثبات الياء في أفعال المضارعة: نحي"
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [ConvertAlifMaksora(), NormalizeHmazat()]
    )
    regs: tuple[str, str] = (
        f"([{uth.hamza}{uth.noon}{uth.yaa}{uth.taa_mabsoota}]{uth.dama}{uth.haa_mohmala}{uth.ras_haaa}{uth.yaa}{uth.kasra})({uth.space}|$)",
        f"\\1{uth.yaa}\\2",
    )


@dataclass
class RemoveKasheeda(ConversionOperation):
    arabic_name: str = "حذف الكشيدة"
    regs: tuple[str, str] = (
        f"{uth.kasheeda}",
        "",
    )


@dataclass
class RemoveHmzatWaslMiddle(ConversionOperation):
    arabic_name: str = "حذف همزة الوصل وصلا"
    regs: tuple[str, str] = (
        f"(?!^){uth.hamzat_wasl}",
        r"",
    )


@dataclass
class RemoveSkoonMostadeer(ConversionOperation):
    arabic_name: str = "حذف الحرف أعلاه سكون مستدير"
    regs: tuple[str, str] = (
        f"(.){uth.skoon_mostadeer}",
        r"",
    )


@dataclass
class SkoonMostateel(ConversionOperation):
    arabic_name: str = "ضبط السكون المستطيل"
    regs: list[tuple[str, str]] = field(
        default_factory=lambda: [
            # remove from the middle
            (
                f"{uth.alif}{uth.skoon_mostateel}{uth.space}",
                f"{uth.space}",
            ),
            # convert to alif at the end
            (
                f"{uth.alif}{uth.skoon_mostateel}$",
                f"{uth.alif}",
            ),
        ]
    )


@dataclass
class MaddAlewad(ConversionOperation):
    arabic_name: str = "ضبط مد العوض وسطا ووقفا"
    regs: list[tuple[str, str]] = field(
        default_factory=lambda: [
            # remove from the middle
            (
                f"({uth.tanween_fath_modgham}|{uth.tanween_fath_iqlab}|{uth.tanween_fath_mothhar}){uth.alif}({uth.space}|$)",
                r"\1\2",
            ),
            # convert to alif at the end
            (
                f"({uth.tanween_fath_modgham}|{uth.tanween_fath_iqlab}|{uth.tanween_fath_mothhar})$",
                f"{uth.fatha}{uth.alif}",
            ),
        ]
    )


@dataclass
class WawAlsalah(ConversionOperation):
    arabic_name: str = "إبدال واو الصلاة ومثيلاتها ألفا"
    regs: tuple[str, str] = (
        f"{uth.waw}{uth.alif_khnjaria}",
        f"{uth.alif}",
    )


@dataclass
class EnlargeSmallLetters(ConversionOperation):
    arabic_name: str = (
        "تكبير الألف والياء والاو والنون الصغار مع حذف مد الصلة عند الوقف"
    )
    regs: list[tuple[str, str]] = field(
        default_factory=lambda: [
            # small alif
            (
                uth.alif_khnjaria,
                uth.alif,
            ),
            # small noon
            (
                uth.small_noon,
                uth.noon,
            ),
            # small waw
            (
                f"{uth.haa}{uth.dama}{uth.small_waw}{uth.madd}?$",
                f"{uth.haa}{uth.dama}",
            ),
            (
                uth.small_waw,
                uth.waw,
            ),
            # Small yaa
            (
                uth.small_yaa,
                uth.small_yaa_sila,
            ),
            (
                f"{uth.haa}{uth.kasra}{uth.small_yaa_sila}{uth.madd}?$",
                f"{uth.haa}{uth.kasra}",
            ),
            (
                uth.small_yaa_sila,
                uth.yaa,
            ),
        ]
    )


@dataclass
class CleanEnd(ConversionOperation):
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            ConvertAlifMaksora(),
            NormalizeHmazat(),
            IthbatYaaYohie(),
            RemoveKasheeda(),
            RemoveSkoonMostadeer(),
            SkoonMostateel(),
            MaddAlewad(),
            WawAlsalah(),
            EnlargeSmallLetters(),
        ]
    )
    arabic_name: str = "تسكين حرف الوقف"
    regs: tuple[str, str] = (
        f"({'|'.join([uth.fatha, uth.dama, uth.kasra, uth.tanween_dam_modgham, uth.tanween_dam_iqlab, uth.tanween_dam_mothhar, uth.tanween_kasr_modgham, uth.tanween_kasr_iqlab, uth.tanween_kasr_mothhar, uth.madd])})$",
        r"",
    )


@dataclass
class NormalizeTaa(ConversionOperation):
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            CleanEnd(),
        ]
    )
    arabic_name: str = "تحويب التاء المربطة في الوسط لتاء وفي الآخر لهاء"
    regs: tuple[str, str] = field(
        default_factory=lambda: [
            (f"{uth.taa_marboota}$", f"{uth.haa}"),
            (f"{uth.taa_marboota}", f"{uth.taa_mabsoota}"),
        ]
    )


@dataclass
class AddAlifIsmAllah(ConversionOperation):
    arabic_name: str = "إضافة ألف مد الطبيعي في اسم الله عز وجل"
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            CleanEnd(),
            NormalizeTaa(),
        ]
    )
    regs: tuple[str, str] = (
        f"({uth.lam}{uth.kasra}?{uth.lam}{uth.shadda}{uth.fatha})({uth.haa}(?:.|$)(?![{uth.baa}{uth.waw}]))",
        f"\\1{uth.alif}\\2",
    )


@dataclass
class PrepareGhonnaIdghamIqlab(ConversionOperation):
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            SpecialCases(),
            RemoveHmzatWaslMiddle(),
            CleanEnd(),
            NormalizeTaa(),
            AddAlifIsmAllah(),
        ]
    )
    arabic_name: str = "فك الإقلاب والعغنة الإدغام"
    regs: tuple[str, str] = field(
        default_factory=lambda: [
            # النون المقلبة ميمام
            (
                f"{uth.noon}{uth.meem_iqlab}",
                f"{uth.meem}",
            ),
            # تنوين الفتح المقبل ميمام
            (
                # f"{uth.tanween_fath_iqlab}",
                # f"{uth.fatha}{uth.meem}",
                f"{uth.tanween_fath}.({uth.space}{uth.baa})",
                f"{uth.fatha}{uth.meem}\\1",
            ),
            #  فك تنوين الضم المقلب
            (
                # f"{uth.tanween_dam_iqlab}",
                # f"{uth.dama}{uth.meem}",
                f"{uth.tanween_dam}.({uth.space}{uth.baa})",
                f"{uth.dama}{uth.meem}\\1",
            ),
            #  فك تنوين الكسر المقلب ميما
            (
                # f"{uth.tanween_kasr_iqlab}",
                # f"{uth.kasra}{uth.meem}",
                f"{uth.tanween_kasr}.({uth.space}{uth.baa})",
                f"{uth.kasra}{uth.meem}\\1",
            ),
            # فك التنوين المدغم
            (
                # f"{uth.tanween_fath_modgham}",
                # f"{uth.fatha}{uth.noon}",
                f"{uth.tanween_fath}.({uth.space}[{uth.noon_ikhfaa_group}{uth.noon_idgham_group}])",
                f"{uth.fatha}{uth.noon}\\1",
            ),
            (
                # f"{uth.tanween_dam_modgham}",
                # f"{uth.dama}{uth.noon}",
                f"{uth.tanween_dam}.({uth.space}[{uth.noon_ikhfaa_group}{uth.noon_idgham_group}])",
                f"{uth.dama}{uth.noon}\\1",
            ),
            (
                # f"{uth.tanween_kasr_modgham}",
                # f"{uth.kasra}{uth.noon}",
                f"{uth.tanween_kasr}.({uth.space}[{uth.noon_ikhfaa_group}{uth.noon_idgham_group}])",
                f"{uth.kasra}{uth.noon}\\1",
            ),
            # فك التنوين المظهر
            (
                f"{uth.tanween_fath_mothhar}",
                f"{uth.fatha}{uth.noon}{uth.ras_haaa}",
            ),
            (
                f"{uth.tanween_dam_mothhar}",
                f"{uth.dama}{uth.noon}{uth.ras_haaa}",
            ),
            (
                f"{uth.tanween_kasr_mothhar}",
                f"{uth.kasra}{uth.noon}{uth.ras_haaa}",
            ),
            # حذف الحرف الأول من الحفران المدغمان
            (
                f"([{uth.fatha}{uth.dama}]{uth.yaa}|[{uth.fatha}{uth.kasra}]{uth.waw}|[{uth.pure_letters_without_yaa_and_waw_group}]){uth.space}?([{uth.pure_letters_group}]{uth.shadda})",
                r"\2",
            ),
        ]
    )


@dataclass
class IltiqaaAlsaknan(ConversionOperation):
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            PrepareGhonnaIdghamIqlab(),
        ]
    )
    arabic_name: str = "التقاء الساكنان وكسر التنوين"
    regs: list[tuple[str, str]] = field(
        default_factory=lambda: [
            # كسر التنوين
            (
                f"({uth.noon}){uth.ras_haaa}({uth.space}.[{uth.ras_haaa}{uth.shadda}])",
                f"\\1{uth.kasra}\\2",
            ),
            # حذف حرف المد الأول لاتقاء الساعكنان
            # alif
            (
                f"{uth.madd_alif}({uth.space}.[{uth.ras_haaa}{uth.shadda}])",
                f"{uth.fatha}\\1",
            ),
            # waw
            (
                f"{uth.madd_waw}({uth.space}.[{uth.ras_haaa}{uth.shadda}])",
                f"{uth.dama}\\1",
            ),
            # yaa
            (
                f"{uth.madd_yaa}({uth.space}.[{uth.ras_haaa}{uth.shadda}])",
                f"{uth.kasra}\\1",
            ),
        ]
    )


@dataclass
class Ghonna(ConversionOperation):
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            IltiqaaAlsaknan(),
            DeleteShaddaAtBeginning(),
        ]
    )
    arabic_name: str = "وضع الغنة في النون الميم"
    regs: tuple[str, str] = ("", "")
    ghonna_len: int = 3
    idgham_yaa_waw_len: int = 2

    def forward(self, text, moshaf: MoshafAttributes) -> str:
        # الميم المخفار
        if moshaf.meem_mokhfah == "meem":
            meem_mokhfah = ph.meem
        elif moshaf.meem_mokhfah == "ikhfaa":
            meem_mokhfah = ph.meem_mokhfah
        else:
            raise ValueError()
        text = re.sub(
            f"{uth.meem}{uth.space}?{uth.baa}",
            f"{meem_mokhfah * self.ghonna_len}{uth.baa}",
            text,
        )

        # إدغام النون في الياء و الواو
        text = re.sub(
            f"{uth.noon}{uth.space}([{uth.yaa}{uth.waw}])",
            r"\1" * (self.idgham_yaa_waw_len + 1),
            text,
        )

        # إخفاء النون
        text = re.sub(
            f"{uth.noon}{uth.space}?([{uth.noon_ikhfaa_group}])",
            f"{ph.noon_mokhfah * self.ghonna_len}\\1",
            text,
        )

        # النون والميم المشددتين
        # العنة المتطرفة
        text = re.sub(
            f"([{uth.meem}{uth.noon}]){uth.shadda}$",
            r"\1" * self.ghonna_len,
            text,
        )
        text = re.sub(
            f"([{uth.meem}{uth.noon}]){uth.shadda}",
            r"\1" * (self.ghonna_len + 1),
            text,
        )

        return text


@dataclass
class Tasheel(ConversionOperation):
    arabic_name: str = "إضافة علامة التسهيل"
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            SpecialCases(),
        ]
    )
    regs: tuple[str, str] = (
        f"{uth.alif}{uth.tasheel_sign}",
        f"{ph.hamza_mosahala}",
    )


@dataclass
class Imala(ConversionOperation):
    arabic_name: str = "فك التسهيل"
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            ConvertAlifMaksora(),
            EnlargeSmallLetters(),
        ]
    )
    regs: tuple[str, str] = (
        f"{uth.imala_sign}{uth.alif}",
        f"{ph.fatha_momala}{ph.alif_momala}{ph.alif_momala}",
    )


@dataclass
class MaddPattern:
    pattern: str
    target: str
    madd: str


@dataclass
class Madd(ConversionOperation):
    arabic_name: str = "فك المد"
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            Ghonna(),
            Tasheel(),
            Imala(),
        ]
    )
    regs: tuple[str, str] = ("", "")
    madd_map: dict = field(
        default_factory=lambda: {
            "fath": MaddPattern(
                pattern=f"({uth.fatha}){uth.alif}",
                target=ph.alif,
                madd=uth.alif,
            ),
            "dam": MaddPattern(
                pattern=f"({uth.dama}){uth.waw}",
                target=ph.waw_madd,
                madd=uth.waw,
            ),
            "kasr": MaddPattern(
                pattern=f"({uth.kasra}){uth.yaa}",
                target=ph.yaa_madd,
                madd=uth.yaa,
            ),
        }
    )

    def forward(self, text, moshaf: MoshafAttributes) -> str:
        # المد المنفصل
        # ها ويا التنبيه
        text = re.sub(
            f"((?:^|{uth.space}|(?:(?:^|{uth.space})[{uth.faa}{uth.waw}{uth.hamza}]{uth.fatha}))[{uth.yaa}{uth.haa}]{uth.fatha}){uth.alif}{uth.madd}({uth.hamza}.(?!{uth.space}))",
            r"\1" + ph.alif * moshaf.madd_monfasel_len + r"\2",
            text,
        )
        # normal
        for k, madd_patt in self.madd_map.items():
            text = re.sub(
                f"{madd_patt.pattern}{uth.madd}({uth.space}{uth.hamza})",
                r"\1" + moshaf.madd_monfasel_len * madd_patt.target + r"\2",
                text,
            )

        # المد المتصل وقفا
        # أقوى السببين
        for k, madd_patt in self.madd_map.items():
            text = re.sub(
                f"{madd_patt.pattern}{uth.madd}({uth.hamza}$)",
                r"\1"
                + max(moshaf.madd_mottasel_waqf, moshaf.madd_aared_len)
                * madd_patt.target
                + r"\2",
                text,
            )

        # المد المنفصل
        for k, madd_patt in self.madd_map.items():
            text = re.sub(
                f"{madd_patt.pattern}{uth.madd}({uth.hamza})",
                r"\1" + moshaf.madd_mottasel_len * madd_patt.target + r"\2",
                text,
            )

        # المد اللازم
        # أوجه العنين
        text = re.sub(
            f"({uth.fatha}){uth.yaa}{uth.madd}",
            r"\1" + (moshaf.madd_yaa_alayn_alharfy - 1) * ph.yaa,
            text,
        )
        # ميم آل عمران
        if moshaf.meem_aal_imran == "wasl_2":
            meema_len = 2
        elif moshaf.meem_aal_imran == "wasl_6":
            meema_len = 6
        else:
            meema_len = 6
        text = re.sub(
            f"({uth.meem}{uth.kasra}){uth.yaa}{uth.madd}({uth.meem}{uth.fatha})",
            r"\1" + ph.yaa_madd * meema_len + r"\2",
            text,
        )

        for k, madd_patt in self.madd_map.items():
            text = re.sub(
                f"{madd_patt.pattern}{uth.madd}(.(?:{uth.shadda}|{uth.ras_haaa}|[{ph.noon}{ph.meem}{ph.noon_mokhfah}]{{2,3}}))",
                r"\1" + 6 * madd_patt.target + r"\2",
                text,
            )

        # المد العارض للسكون
        for k, madd_patt in self.madd_map.items():
            text = re.sub(
                f"{madd_patt.pattern}([^{uth.shadda}](?:{uth.ras_haaa}$|$|{ph.sakt}))",
                r"\1" + moshaf.madd_aared_len * madd_patt.target + r"\2",
                text,
            )

        # مد اللين
        text = re.sub(
            f"({uth.fatha})([{uth.yaa}{uth.waw}]){uth.ras_haaa}?([^{uth.shadda}]{uth.ras_haaa}?$)",
            r"\1" + (moshaf.madd_alleen_len - 1) * r"\2" + r"\3",
            text,
        )

        # المد الطبيعي
        for k, madd_patt in self.madd_map.items():
            text = re.sub(
                f"{madd_patt.pattern}(?![{madd_patt.madd}{uth.ras_haaa}{uth.shadda}{uth.harakat_group}])",
                r"\1" + 2 * madd_patt.target,
                text,
            )

        return text


@dataclass
class Qalqla(ConversionOperation):
    arabic_name: str = "إضافة علامة القلقة"
    regs: tuple[str, str] = (
        f"([{uth.qlqla_group}](?:{uth.shadda}$|{uth.ras_haaa}|$))",
        r"\1" + ph.qlqla,
    )
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            CleanEnd(),
        ]
    )


@dataclass
class RemoveRasHaaAndShadda(ConversionOperation):
    arabic_name: str = "حذف السكون والشدة م تكرار الحرف المشدد"
    regs: list[tuple[str, str]] = field(
        default_factory=lambda: [
            # shadda
            (
                f"(.){uth.shadda}",
                r"\1\1",
            ),
            # skoon
            (
                f"{uth.ras_haaa}",
                r"",
            ),
        ]
    )
    ops_before: list[ConversionOperation] = field(
        default_factory=lambda: [
            CleanEnd(),
        ]
    )


OPERATION_ORDER = [
    DisassembleHrofMoqatta(),
    SpecialCases(),
    BeginWithHamzatWasl(),
    BeginWithSaken(),
    ConvertAlifMaksora(),
    NormalizeHmazat(),
    IthbatYaaYohie(),
    RemoveKasheeda(),
    RemoveHmzatWaslMiddle(),
    RemoveSkoonMostadeer(),
    SkoonMostateel(),
    MaddAlewad(),
    WawAlsalah(),
    EnlargeSmallLetters(),
    CleanEnd(),
    NormalizeTaa(),
    AddAlifIsmAllah(),
    PrepareGhonnaIdghamIqlab(),
    IltiqaaAlsaknan(),
    DeleteShaddaAtBeginning(),
    Ghonna(),
    Tasheel(),
    Imala(),
    Madd(),
    Qalqla(),
    RemoveRasHaaAndShadda(),
]
