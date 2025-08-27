class MSE:
    def __call__(self, logits, Y):
        return ((logits - Y) ** 2).mean()
