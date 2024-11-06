import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1])

# 关闭整个坐标轴，包括轴线、刻度和标签
ax.axis('off')

plt.show()
