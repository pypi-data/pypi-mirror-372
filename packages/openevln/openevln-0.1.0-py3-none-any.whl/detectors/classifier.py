class Classifier:
    def __init__(self, model, labels):
        self.model = model
        self.labels = labels

    def analyze(self, text: str) -> dict:
        probabilities = self.model.predict_proba([text])[0]

        return {
            "proba": {
                self.labels[i]: float(probabilities[i]) for i in range(len(self.labels))
            }
        }
