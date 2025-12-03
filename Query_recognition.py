from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


class Query:
    config = {
        "intents": {
            "greeting": {
                "examples": ["привет", "здравствуй", "добрый день",]
            },
            "farewell": {
                "examples": ["пока", "до свидания", "увидимся", "до встречи"]
            },
            "time": {
                "examples": ["время", "сколько времени", "сколько показывают часы",
                             "goodbye", "bye", "see you soon"],
            },

        },
    }

    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
        self.classifier_probability = LogisticRegression()
        self.classifier = LinearSVC()
        self.prepare_corpus()

    def get_intent(self, request):
        best_intent = self.classifier.predict(self.vectorizer.transform([request]))[0]
        index_of_best_intent = list(self.classifier_probability.classes_).index(best_intent)
        probabilities = self.classifier_probability.predict_proba(self.vectorizer.transform([request]))[0]
        best_intent_probability = probabilities[index_of_best_intent]
        if best_intent_probability > 0.157:
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
