import datetime

KHMER_MONTHS = [
    "មករា", "កម្ភៈ", "មីនា", "មេសា", "ឧសភា",
    "មិថុនា", "កក្កដា", "សីហា", "កញ្ញា",
    "តុលា", "វិច្ឆិកា", "ធ្នូ"
]

def date_to_khmer(date: datetime.date) -> str:
    return f"{date.day} {KHMER_MONTHS[date.month-1]} {date.year}"
