class MSE:
    """Mean Squared Error Loss"""
    def __call__(self, probabilities, Y):
        return ((probabilities - Y) ** 2).mean()

class CCE:
    """Categorical Cross Entropy Loss"""
    def __call__(self, probabilities, Y):
        return probabilities.cce(Y)
