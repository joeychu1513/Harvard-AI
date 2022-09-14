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

    # The function should return the joint probability of all of those events taking place.

    set_all_people = set(dict.keys(people))

    set_one_gene = one_gene
    set_two_gene = two_genes
    set_no_gene = set_all_people.difference(set_one_gene).difference(set_two_gene)
    list_set_gene = [set_no_gene, set_one_gene, set_two_gene]

    set_have_trait = have_trait
    set_no_trait = set_all_people.difference(set_have_trait)

    joint_proba = 1

    def get_1_gene(person, one_gene, two_genes):

        father = people[person]["father"]
        mother = people[person]["mother"]

        parents_proba = {father: "", mother: ""}

        for parent in parents_proba:

            # proba of getting 1 gene from parent
            if parent in two_genes:
                parents_proba[parent] = 1 - PROBS["mutation"]
            elif parent in one_gene:
                parents_proba[parent] = 0.5 * PROBS["mutation"] + 0.5 * (1 - PROBS["mutation"])
            else:
                parents_proba[parent] = PROBS["mutation"]

        return parents_proba[father], parents_proba[mother]

    for person in set_all_people:

        # if no parent in input
        if people[person]["mother"] is None and people[person]["father"] is None:
            
            # * proba of gene
            for i, sett in enumerate(list_set_gene):
                if not person in sett:
                    continue # to next set
                else:
                    joint_proba *= PROBS["gene"][i]
                    break

        # if both parent in input
        else:
            proba_father_1, proba_mother_1 = get_1_gene(person, one_gene, two_genes)

            # no gene: get 0 from father AND get 0 from mother
            if person in set_no_gene:
                joint_proba *= (1 - proba_father_1) * (1 - proba_mother_1)
            # one gene: (get 0 from father AND get 1 from mother) OR (get 0 from father AND get 1 from mother)
            elif person in set_one_gene:
                joint_proba *= (proba_father_1 * (1 - proba_mother_1) + (1 - proba_father_1) * proba_mother_1)
            # two genes: get 1 from father AND get 1 from mother
            else:
                joint_proba *= proba_father_1 * proba_mother_1

        # * proba of trait, given gen
        for i, sett in enumerate(list_set_gene):
            if not person in sett:
                continue # to next sett
            elif person in set_have_trait:
                joint_proba *= PROBS["trait"][i][True]
                break
            else:
                joint_proba *= PROBS["trait"][i][False]
                break

    return joint_proba


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    all_name = set(dict.keys(probabilities))
    
    # given one_gene, two_genes, have_trait, add p to corresponding case

    for name in all_name:

        # add to "gene"
        if name in one_gene:
            probabilities[name]["gene"][1] += p
        elif name in two_genes:
            probabilities[name]["gene"][2] += p
        else:
            probabilities[name]["gene"][0] += p
        
        # add to trait
        if name in have_trait:
            probabilities[name]["trait"][True] += p
        else:
            probabilities[name]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    all_name = set(dict.keys(probabilities))

    for name in all_name:
        pre_normal_sum_gene = (
            probabilities[name]["gene"][0]
            + probabilities[name]["gene"][1]
            + probabilities[name]["gene"][2]
        )

        pre_normal_sum_trait = (
            probabilities[name]["trait"][True]
            + probabilities[name]["trait"][False]
        )
        
        for item in probabilities[name]["gene"]:
            probabilities[name]["gene"][item] /= pre_normal_sum_gene
        for item in probabilities[name]["trait"]:
            probabilities[name]["trait"][item] /= pre_normal_sum_trait


if __name__ == "__main__":
    main()
