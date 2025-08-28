def eng_to_khmer_number(num: int) -> str:
    mapping = {'0':'០','1':'១','2':'២','3':'៣','4':'៤','5':'៥','6':'៦','7':'៧','8':'៨','9':'៩'}
    return ''.join(mapping.get(d, d) for d in str(num))

def khmer_to_eng_number(khmer_num: str) -> str:
    mapping = {'០':'0','១':'1','២':'2','៣':'3','៤':'4','៥':'5','៦':'6','៧':'7','៨':'8','៩':'9'}
    return ''.join(mapping.get(d, d) for d in khmer_num)
