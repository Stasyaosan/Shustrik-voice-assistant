import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


class Query:

    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            Query.config = json.load(f)

        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
        self.classifier_probability = LogisticRegression()
        self.classifier = LinearSVC()
        self.prepare_corpus()

    def get_intent(self, request):
        best_intent = self.classifier.predict(self.vectorizer.transform([request]))[0]
        index_of_best_intent = list(self.classifier_probability.classes_).index(best_intent)
        probabilities = self.classifier_probability.predict_proba(self.vectorizer.transform([request]))[0]
        best_intent_probability = probabilities[index_of_best_intent]
        if best_intent_probability > 0.23:
            return best_intent

    def prepare_corpus(self):
        corpus = []
        target_vector = []
        for intent_name, intent_data in Query.config["intents"].items():
            for example in intent_data["examples"]:
                corpus.append(example)
                target_vector.append(intent_name)
        training_vector = self.vectorizer.fit_transform(corpus)
        self.classifier_probability.fit(training_vector, target_vector)
        self.classifier.fit(training_vector, target_vector)
