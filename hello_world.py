motorcycles = [] 
print(motorcycles)

motorcycles.append('honda') 
motorcycles.append('yamaha') 
motorcycles.append('suzuki')
motorcycles.append('ducati')
print(motorcycles)

motorcycles.insert(0, 'BYD')
motorcycles.remove('ducati')
print(motorcycles)

popped_motorcycle = motorcycles.pop()
print(motorcycles)
print(popped_motorcycle)
print(motorcycles[-1])