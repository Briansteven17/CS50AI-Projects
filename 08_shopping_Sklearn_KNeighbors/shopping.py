import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    evidences = []
    labels = []

    months = {'Feb': 1, 'Mar': 2, 'May': 4, 'Oct': 9, 'June': 5, 'Jul': 6, 'Aug': 7, 'Nov': 10, 'Sep': 8, 'Dec': 11}

    with open(filename) as shopping_data:
        reader = csv.reader(shopping_data)
        
        count_rows = 0
        int_columns = (1, 3, 5, 12, 13, 14, 15)
        float_columns = (2, 4, 6, 7, 8, 9 , 10)
        special_variable = (16, 17, 18)

        for row in reader:
            if count_rows == 0:
                count_rows += 1
                continue
            count = 0
            evidence = []
            for variable in row:
                count += 1
                if count in int_columns:
                    evidence.append(int(variable))
                elif count in float_columns:
                    evidence.append(float(variable))
                elif count == 11:
                    for month_number in range(12):
                        if month_number == months[variable]:
                            evidence.append(month_number)
                            break
                elif count in special_variable:
                    if variable == "Returning_Visitor" or variable == "TRUE":
                        if count == 18:
                            labels.append(1)
                        else:
                            evidence.append(1)
                    elif variable == "New_Visitor" or variable == "FALSE" or variable == "Other": # Check other
                        if count == 18:
                            labels.append(0)
                        else:
                            evidence.append(0) 
                    else:
                        print(count)
                        print("not match")
            evidences.append(evidence)

    return (evidences, labels)



def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    kneighbor = KNeighborsClassifier(n_neighbors=1)
    result = kneighbor.fit(evidence, labels)

    return result



def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    if len(labels) != len(predictions):
        print("Labels and predictions different len")

    true_predicted = 0
    not_true_predicted = 0

    negative_predicted = 0
    not_negative_predicted = 0


    for i in range(len(labels)):
        if labels[i] == 1:
            if int(labels[i]) == int(predictions[i]):
                true_predicted += 1
            else:
                not_true_predicted += 1
        elif labels[i] == 0:
            if int(labels[i]) == int(predictions[i]):
                negative_predicted += 1
            else:
                not_negative_predicted += 1

    sensitivity = true_predicted/(true_predicted + not_true_predicted)
    specificity = negative_predicted/(negative_predicted + not_negative_predicted)

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
