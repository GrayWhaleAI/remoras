
class GeniusValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"Unable to validate Genius Item/Instruction: {self.message}"
    
        

    
