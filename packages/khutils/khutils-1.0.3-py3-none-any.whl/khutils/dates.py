from decimal import Decimal
from datetime import datetime, date

class EnglishToKhmerUtil:
    KHMER_NUMERALS = {
        "0": "០", "1": "១", "2": "២", "3": "៣", "4": "៤",
        "5": "៥", "6": "៦", "7": "៧", "8": "៨", "9": "៩"
    }

    KHMER_MONTHS = {
        1: "មករា", 2: "កុម្ភៈ", 3: "មីនា", 4: "មេសា", 5: "ឧសភា", 6: "មិថុនា",
        7: "កក្កដា", 8: "សីហា", 9: "កញ្ញា", 10: "តុលា", 11: "វិច្ឆិកា", 12: "ធ្នូ"
    }

    KHMER_WEEKDAYS = {
        0: "ច័ន្ទ", 1: "អង្គារ", 2: "ពុធ", 3: "ព្រហស្បតិ៍", 4: "សុក្រ", 5: "សៅរ៍", 6: "អាទិត្យ"
    }
    
    @classmethod
    def _validate_number(cls, number):
        if not isinstance(number, (int, float, Decimal, str)):
            raise Exception("Invalid Type: Expected int, float, Decimal or str")
    
    @classmethod
    def _to_khmer_numeral(cls, value):
        return ''.join(cls.KHMER_NUMERALS.get(d, d) for d in str(value))
        
    @classmethod
    def convert_number_to_khmer(cls, number):
        cls._validate_number(number)        
        return cls._to_khmer_numeral(number)

    @classmethod
    def khmer_numeral_format(cls, number):
        cls._validate_number(number)
        return cls._to_khmer_numeral(number)

    @classmethod
    def format_english_to_khmer_date(cls, date_input, is_include_day_name=False, is_include_time=False, is_has_label=True, kh_date_format="d M Y"):
        if isinstance(date_input, str):
            date_input = datetime.fromisoformat(date_input)
        if isinstance(date_input, date) and not isinstance(date_input, datetime):
            date_input = datetime.combine(date_input, datetime.min.time())
            
        day = cls.khmer_numeral_format(date_input.day)
        month = cls.KHMER_MONTHS[date_input.month]
        year = cls.khmer_numeral_format(date_input.year)
        weekday = cls.KHMER_WEEKDAYS[date_input.weekday()]
        hour = cls.khmer_numeral_format(date_input.hour)
        minute = cls.khmer_numeral_format(date_input.minute)
        time_str = f"{hour}:{minute}"

        if is_has_label:
            if is_include_day_name:
                day = f"ទី {day}"
            else:
                day = f"ថ្ងៃទី {day}"
            month = f"ខែ {month}"
            year = f"ឆ្នាំ {year}"
            if is_include_day_name:
                weekday = f"ថ្ងៃ {weekday}"
            time_str = f"{hour}:{minute} នាទី"

        result = kh_date_format.replace("d", day).replace("M", month).replace("Y", year)

        if is_include_day_name:
            result = f"{weekday} {result}"

        if is_include_time:
            result = f"{result} {time_str}"

        return result
    
    @classmethod
    def number_to_word(cls, number, is_remove_rounding_kh=False, remove_rounding_kh=2): 
        if number is None:
            raise Exception("Number cannot be None")
        
        if isinstance(number, str):
            try:
                number = float(number)
            except ValueError:
                raise ValueError("Input string must be a valid number")

        if is_remove_rounding_kh:
            formatted = f"{number:.{remove_rounding_kh}f}"
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            number_str = formatted
        else:
            number_str = str(number)

        raw_word_en = num2words(float(number_str))
        en_words = [
            word.capitalize() if word.lower() != "and" else word
            for word in raw_word_en.split()
        ]
        
        concate_word_in_en = " ".join(en_words)
        convert_word_in_en = concate_word_in_en.replace(",", "")
        convert_word_in_kh = tha.cardinals.processor(number_str).replace("_", "").replace("▁", "").strip()
        
        return {
            "word_in_en": convert_word_in_en,
            "word_in_kh": convert_word_in_kh
        }