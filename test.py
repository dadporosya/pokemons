import requests
url = "https://pokeapi.co/api/v2/pokemon/"
n = 1000
heights = [0] * n
weights = [0] * n
for i in range(1, n):
    response = requests.get(url + str(i))
    # print(i, end=", ")
    # if response.status_code == 200:
    data = response.json()
    heights[i] = (data["height"])
    weights[i] = (data["weight"])

print()

print(f"heights\n"
      f"min: f{min(heights)}, max: {max(heights)}, avr: {sum(heights)/n}")

print(f"weights\n"
      f"min: f{min(weights)}, max: {max(weights)}, avr: {sum(weights)/n}")

# heights
# min: 0, max: 200, avr: 11.976
# weights
# min: 0, max: 9999, avr: 646.016