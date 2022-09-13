import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    person_p = dict()

    for person in people:
        if people[person]["mother"] == None and people[person]["father"] == None:
            if person in one_gene:
                genes = 1
            elif person in two_genes:
                genes = 2          
            else:
                genes = 0
            copy_p = PROBS["gene"][genes]
            if person in have_trait:
                person_p[person] = copy_p * PROBS["trait"][genes][True] 
            else:
                person_p[person] = copy_p * PROBS["trait"][genes][False] 
    
    for son in people:
        dad_p = 0
        mom_p = 0
        son_AB = 0
        son_genes = 0
        if people[son]["mother"] != None and people[son]["father"] != None:
            mom = people[son]["mother"] 
            dad = people[son]["father"]
            mutation = PROBS["mutation"]

            for parent in people:
                if parent == dad or parent == mom:
                    # mom and dad probabilties of pass one of their genes (the bad one)
                    if parent == dad and dad in one_gene:
                        dad_p = (1 - mutation) * 0.5 # maybe change the way 0.5 is multiplying
                    elif parent == dad and dad in two_genes:
                        dad_p = 1 - mutation
                    elif parent == dad: 
                        dad_p = mutation
                    elif parent == mom and mom in one_gene:
                        mom_p = (1 - mutation) * 0.5
                    elif parent == mom and mom in two_genes:
                        mom_p = 1 - mutation
                    elif parent == mom:
                        mom_p = mutation
                # Probability that child get 0, 1 or 2 genes from their parents
                if  dad_p != 0 and mom_p != 0:
                    if son in two_genes:
                        son_AB = dad_p * mom_p # if not work, check
                        son_genes = 2
                    elif son in one_gene: 
                        son_AB = (dad_p * (1 - mom_p)) + (mom_p * (1 - dad_p)) 
                        son_genes = 1
                    else:
                        son_AB = (1 - dad_p) * (1 - mom_p) # if not work, check
                        son_genes = 0
                 
                    if son in have_trait:
                        person_p[son] = son_AB * PROBS["trait"][son_genes][True]
                    else:
                        person_p[son] = son_AB * PROBS["trait"][son_genes][False]

                    break
        if len(person_p) == len(people):
            break
                   
    joint_proba = 1
    for person in person_p:
        joint_proba *= person_p[person]
 
    return joint_proba

    #raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    #raise NotImplementedError

    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    #print(probabilities)
    for person in probabilities:
        gene_2 = probabilities[person]["gene"][2]
        gene_1 = probabilities[person]["gene"][1]
        gene_0 = probabilities[person]["gene"][0]

        total_gene = gene_0 + gene_1 + gene_2
        probabilities[person]["gene"][0] = gene_0/total_gene
        probabilities[person]["gene"][1] = gene_1/total_gene
        probabilities[person]["gene"][2] = gene_2/total_gene

        true = probabilities[person]["trait"][True]
        false = probabilities[person]["trait"][False]

        total_bool = true + false
        probabilities[person]["trait"][True] = true/total_bool
        probabilities[person]["trait"][False] = false/total_bool

    #raise NotImplementedError


if __name__ == "__main__":
    main()
