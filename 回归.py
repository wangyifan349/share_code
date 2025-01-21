import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 生成示例数据
np.random.seed(0)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# 创建线性回归模型并进行拟合
lin_reg = LinearRegression()
lin_reg.fit(X, y)

# 进行预测
X_new = np.array([[0], [2]])
y_predict = lin_reg.predict(X_new)

# 绘制结果
plt.scatter(X, y, color='blue', label='Data points')
plt.plot(X_new, y_predict, color='red', linewidth=2, label='Linear fit')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Linear Regression')
plt.legend()
plt.show()

print(f"Coefficients: {lin_reg.coef_}")
print(f"Intercept: {lin_reg.intercept_}")


import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# 生成示例数据
np.random.seed(0)
X = 6 * np.random.rand(100, 1) - 3
y = 0.5 * X**2 + X + 2 + np.random.randn(100, 1)

# 创建多项式特征
poly_features = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly_features.fit_transform(X)

# 创建线性回归模型并进行拟合
poly_reg = LinearRegression()
poly_reg.fit(X_poly, y)

# 进行预测
X_new = np.linspace(-3, 3, 100).reshape(100, 1)
X_new_poly = poly_features.transform(X_new)
y_new = poly_reg.predict(X_new_poly)

# 绘制结果
plt.scatter(X, y, color='blue', label='Data points')
plt.plot(X_new, y_new, color='red', linewidth=2, label='Polynomial fit')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Polynomial Regression')
plt.legend()
plt.show()

print(f"Coefficients: {poly_reg.coef_}")
print(f"Intercept: {poly_reg.intercept_}")



