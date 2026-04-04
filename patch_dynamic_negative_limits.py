from pathlib import Path

path = Path('logica_ciudad.py')
text = path.read_text(encoding='utf-8')
old = '''        # Restar consumo pero no dejar muy negativo
        self.recursos["comida"] -= consumo_comida
        self.recursos["agua"] -= consumo_agua
        
        # Clampear para evitar números muy grandes negativos
        self.recursos["comida"] = max(self.recursos["comida"], -500)
        self.recursos["agua"] = max(self.recursos["agua"], -500)

        noticias_sucias = []
'''
new = '''        # Restar consumo pero no dejar muy negativo
        self.recursos["comida"] -= consumo_comida
        self.recursos["agua"] -= consumo_agua
        
        # Clampear según el límite dinámico negativo por recurso
        self.recursos["comida"] = max(self.recursos["comida"], -(self.max_comida // 2))
        self.recursos["agua"] = max(self.recursos["agua"], -(self.max_agua // 2))
        self.recursos["electricidad"] = max(self.recursos["electricidad"], -(self.max_energia // 2))

        noticias_sucias = []
'''
count = text.count(old)
print('found', count, 'occurrences')
if count == 0:
    raise ValueError('old block not found')
text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
print('replaced')
