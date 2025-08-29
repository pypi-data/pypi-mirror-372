from arts import Dict_file

stock = Dict_file(f"{__file__}/../ig_test.json")

stock['hat'] = 10
stock['shoe'] = 20
stock['jacket'] = 30

stock['jacket'] = 31

jacket_count = stock['jacket']

mouse_count = stock.get('mouse', default=0)

shoe_count = stock.pop('shoe')

mouse_count = mouse_count = stock.pop('mouse', 0)