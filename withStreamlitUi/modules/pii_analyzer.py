from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
class PIIAnalyzer:
    """Analyzes text for PII using Presidio."""
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.add_custom_recognizers()

    def add_custom_recognizers(self):
        aadhaar_pattern = Pattern("Aadhaar Number", r"\b\d{4}\s?\d{4}\s?\d{4}\b", 0.9)
        phone_pattern = Pattern("Indian Phone Number", r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b", 0.85)
        address_pattern = Pattern("Indian Address",
                                   r"\b(?:\d{1,4}[,.\-\/\s]?[a-zA-Z0-9\s]+[,.\-\/\s]?)?\b(?:[a-zA-Z\s]+[,.\-\/\s]?)?\b\d{6}\b", 0.8)

        self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="IND_AADHAAR", patterns=[aadhaar_pattern]))
        self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="IND_PHONE", patterns=[phone_pattern]))
        self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="IND_ADDRESS", patterns=[address_pattern]))

    def classify_text(self, text):
        results = self.analyzer.analyze(text=text, entities=[], language='en')
        print("Entities Detected:")
        for result in results : 
            start = result.start
            end = result.end
            word = text[start:end]
            print(f" - {result.entity_type}: {word} (confidence: {result.score:.2f})")
            #print(entity)
                
        return [
            {"entity": result.entity_type, "start": result.start, "end": result.end, "score": result.score}
            for result in results #if result.score >= 0.60
        ]
    
    

