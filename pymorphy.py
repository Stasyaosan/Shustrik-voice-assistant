from pymorphy3 import MorphAnalyzer

morph = MorphAnalyzer()

apple = morph.parse('яблоко')[0]

print(apple.make_agree_with_number(1).word)  # яблоко
print(apple.make_agree_with_number(2).word)  # яблока
print(apple.make_agree_with_number(22).word)  # яблок
