import csv
from typing import (
    Dict,
    List,
)
import random


filename = 'ChatGPT-evaluation-v2.txt'


def take_n_random_elements(data: List, n: int) -> List:
    """Take n random elements from a list of data"""
    return random.sample(data, n)

class Evaluation:
    """Class to store the evaluation of an argument"""

    claim: int
    claim_premise: int = None
    aspect: int = None
    premise_validation: int = None
    coherence: int = None
    consistence: int = None
    persuasion: int = None
    emotional_ethic: int = None

    def __init__(self, claim: str, claim_premise: str, aspect: str, premise_validation: str, coherence: str, consistence: str, persuasion: str, emotional_ethic: str) :
        """Initialize the evaluation of an argument"""
        self.claim = int(claim)
        if claim == '1':
            self.claim_premise = int(claim_premise)
            self.aspect = int(aspect)
            if claim_premise == '1':
                self.premise_validation = int(premise_validation)
                self.coherence = int(coherence)
                self.consistence = int(consistence)
                self.persuasion = int(persuasion)
                self.emotional_ethic = int(emotional_ethic)

    def get_field(self, field_name: str) -> int:
        """Get the value of a field of the evaluation"""
        return getattr(self, field_name)
    
    def format_print(self):
        """Format the evaluation to print it in a human-readable way"""
        cad = "Claim: " + str(self.claim) + ', Claim+premise: ' + str(self.claim_premise) + ', Aspect related: ' + str(self.aspect) + ', Premise validation: ' + str(self.premise_validation) + ', Coherence: ' + str(self.coherence) + ', Consistence: ' + str(self.consistence) + ', Persuasion: ' + str(self.persuasion) + ', Emotional/ethic: ' + str(self.emotional_ethic)
        return cad
    
    def format_file(self, fields: List[str]):
        """Format the evaluation to save it in a file with the specified fields"""
        cad = '\t'.join([str(self.get_field(field)) for field in fields])
        return cad
        
    
class EvaluatedArgument:
    """Class to store an argument with its evaluation"""

    def __init__(self, id_proposal: int, id_argument: int, argument: str, evaluation: Evaluation):
        """Initialize the argument with its evaluation"""
        self.id_proposal = id_proposal
        self.id_argument = id_argument
        self.argument = argument
        self.evaluation = evaluation

    def get_evaluation(self):
        """Get the evaluation of the argument"""
        return self.evaluation
    def format_print(self):
        """Format the argument to print it in a human-readable way"""
        cad = "\tArgument id: " + str(self.id_argument) + '\n\tArgument: ' + self.argument + '\n\tEvaluation: ' + self.evaluation.format_print() + '\n\n'
        return cad
    def format_file(self, fields: List[str]):
        """Format the argument to save it in a file with the specified fields"""
        cad = str(self.id_argument) + '\t' + self.argument + '\t'+ self.evaluation.format_file(fields)
        return cad
    
class Corpus:
    """Class to store a corpus of arguments with their evaluations"""

    arguments_dict: Dict[int, List[EvaluatedArgument]]

    def __init__(self):
        """Initialize the corpus of arguments"""
        self.arguments_dict = {}

    def _append_argument(self, proposal_id: int,argument: EvaluatedArgument):
        """Append an argument to the corpus of arguments"""
        if proposal_id in self.arguments_dict:
            self.arguments_dict[proposal_id].append(argument)
        else:
            self.arguments_dict[argument.id_proposal] = [argument]

    def append_all_arguments(self, proposal_id: int, arguments: List[EvaluatedArgument]):
        """Append a list of arguments to the corpus of arguments"""
        for argument in arguments:
            self._append_argument(proposal_id, argument)
    
    def filter_by_completed(self, field_name: str, value: int):
        """Filter the corpus of arguments by the value of a field of the evaluation of the arguments, completed with the same number of non-arguments"""
        filtered_corpus = Corpus()
        for proposal_id in self.arguments_dict.keys():
            arguments = self.arguments_dict[proposal_id]
            arguments = [argument for argument in arguments if argument.get_evaluation().get_field(field_name) == value]
            number_filtered = len(arguments)
            filtered_corpus.append_all_arguments(proposal_id, arguments)
            non_arguments = self.arguments_dict[proposal_id]
            non_arguments = [argument for argument in non_arguments if argument.get_evaluation().get_field('claim_premise') != 1]
            non_arguments = take_n_random_elements(non_arguments, number_filtered)
            filtered_corpus.append_all_arguments(proposal_id, non_arguments)
        return filtered_corpus
    
    def format_print(self):
        """Format the corpus of arguments to print it in a human-readable way"""
        cad = ""
        for proposal_id in self.arguments_dict.keys():
            cad += ("Proposal id: " + str(proposal_id) + '\n\n')
            arguments = self.arguments_dict[proposal_id]
            for argument in arguments:
                cad += argument.format_print()

        return cad

    def format_file(self, fields: List[str]):
        """Format the corpus of arguments to save it in a file with the specified fields"""
        cad = "proposal_id\targument_id\targument\t" + '\t'.join(fields) + "\n"
        for proposal_id in self.arguments_dict.keys():
            arguments = self.arguments_dict[proposal_id]
            for argument in arguments:
                cad += str(proposal_id) + '\t' + argument.format_file(fields) + '\n'
        return cad
    
    def save_to_file(self, filename: str, fields: List[str] = ['claim', 'claim_premise', 'aspect', 'premise_validation', 'coherence', 'consistence', 'persuasion', 'emotional_ethic']):
        """Save the corpus of arguments in a file with the specified fields"""
        with open(filename, 'w', encoding = 'utf-8') as file:
            file.write(self.format_file(fields))

    
    def filter_by(self, field_name: str, value: int):
        """Filter the corpus of arguments by the value of a field of the evaluation of the arguments"""
        filtered_corpus = Corpus()
        for proposal_id in self.arguments_dict.keys():
            arguments = self.arguments_dict[proposal_id]
            arguments = [argument for argument in arguments if argument.get_evaluation().get_field(field_name) == value]
            filtered_corpus.append_all_arguments(proposal_id, arguments)
        return filtered_corpus

#optimized, only one iteration
def classify_arguments_or_not_opt():
    """Classify the arguments as arguments or not arguments based on the value of the field 'Claim+premise?WHY?' of the evaluation of the arguments"""
    proposal_id = -1
    corpus = Corpus()
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['Tipo elemento'] != 'Argumento':
                continue
            if row['Id propuesta'] != proposal_id:
                if proposal_id != -1:
                    eval_args_number = len(evaluated_data)
                    non_evaluated_args_number = len(non_evaluated_data)
                    if eval_args_number < non_evaluated_args_number:
                        non_evaluated_data = take_n_random_elements(non_evaluated_data, eval_args_number)
                    elif non_evaluated_args_number < eval_args_number:
                        evaluated_data = take_n_random_elements(evaluated_data, non_evaluated_args_number)
                    corpus.append_all_arguments(proposal_id, evaluated_data)
                    corpus.append_all_arguments(proposal_id, non_evaluated_data)
                proposal_id = int(row['Id propuesta'])
                evaluated_data = []    
                non_evaluated_data = []   
            evaluation = Evaluation(row['Claim?'], row['Claim+premise?\nWHY?'], row['Relacionado con aspecto?'], row['Validación premisa(s)'], row['Coherencia lógica p->c'], row['Consistencia p1 <> p2'], row['Persuasión'], row['Apelación emocioal/ética (pathos/ethos)'])
            evaluated_argument = EvaluatedArgument(proposal_id, int(row['Id elemento']), row['Valor'], evaluation)
            if row['Claim+premise?\nWHY?'] == 1:
                evaluated_data.append(evaluated_argument)
            else:
                non_evaluated_data.append(evaluated_argument)
        return corpus
    
#optimized, only one iteration
def classify_arguments_or_not_with_aspect_opt():
    """Classify the arguments as arguments or not arguments based on the value of the fields 'Claim+premise?WHY?' and 'Relacionado con aspecto?' of the evaluation of the arguments"""
    proposal_id = -1
    corpus = Corpus()
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['Tipo elemento'] != 'Argumento':
                continue
            if row['Id propuesta'] != proposal_id:
                if proposal_id != -1:
                    eval_args_number = len(evaluated_data)
                    non_evaluated_args_number = len(non_evaluated_data)
                    if eval_args_number < non_evaluated_args_number:
                        non_evaluated_data = take_n_random_elements(non_evaluated_data, eval_args_number)
                    elif non_evaluated_args_number < eval_args_number:
                        evaluated_data = take_n_random_elements(evaluated_data, non_evaluated_args_number)
                    corpus.append_all_arguments(proposal_id, evaluated_data)
                    corpus.append_all_arguments(proposal_id, non_evaluated_data)
                proposal_id = int(row['Id propuesta'])
                evaluated_data = []    
                non_evaluated_data = []   
            evaluation = Evaluation(row['Claim?'], row['Claim+premise?\nWHY?'], row['Relacionado con aspecto?'], row['Validación premisa(s)'], row['Coherencia lógica p->c'], row['Consistencia p1 <> p2'], row['Persuasión'], row['Apelación emocioal/ética (pathos/ethos)'])
            evaluated_argument = EvaluatedArgument(proposal_id, int(row['Id elemento']), row['Valor'], evaluation)
            if row['Claim+premise?\nWHY?'] == 1 and row['Relacionado con aspecto?'] == '1':
                evaluated_data.append(evaluated_argument)
            elif row['Claim+premise?\nWHY?'] != 1:
                non_evaluated_data.append(evaluated_argument)
        return corpus

#not optimized, two iterations
def classify_arguments_or_not():
    """Classify the arguments as arguments or not arguments based on the value of the field 'Claim+premise?WHY?' of the evaluation of the arguments"""
    corpus = create_complete_corpus()
    filtered_corpus = corpus.filter_by('claim_premise', 1)
    return filtered_corpus

#not optimized, two iterations
def classify_arguments_or_not_with_aspect():
    """Classify the arguments as arguments or not arguments based on the value of the fields 'Claim+premise?WHY?' and 'Relacionado con aspecto?' of the evaluation of the arguments"""
    corpus = create_complete_corpus()
    filtered_corpus = corpus.filter_by('claim_premise', 1).filter_by('aspect', 1)
    return filtered_corpus

def create_complete_corpus():
    """Create a corpus with all the arguments and non-arguments"""
    proposal_id = -1
    corpus = Corpus()
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['Tipo elemento'] != 'Argumento':
                continue
            if row['Id propuesta'] != proposal_id:
                if proposal_id != -1:
                    corpus.append_all_arguments(proposal_id, data)
                proposal_id = int(row['Id propuesta'])
                data = []    
            evaluation = Evaluation(row['Claim?'], row['Claim+premise?\nWHY?'], row['Relacionado con aspecto?'], row['Validación premisa(s)'], row['Coherencia lógica p->c'], row['Consistencia p1 <> p2'], row['Persuasión'], row['Apelación emocioal/ética (pathos/ethos)'])
            evaluated_argument = EvaluatedArgument(proposal_id, int(row['Id elemento']), row['Valor'], evaluation)
            data.append(evaluated_argument)
        return corpus



        
    