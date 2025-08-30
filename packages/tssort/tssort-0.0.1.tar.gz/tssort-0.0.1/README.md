This repository contains and implementation of the TSSort algorithm proposed in "TSSort – Probabilistic Noise Resistant Sorting" (Hees et al., 2011).

# Expected Input
This module expects a text file with a list of sentences separated by newline and a text file of a list of pairwise comparisons in the form int,int and separated by newline. See the sample data files ```comparisons.txt``` and ```sentences.txt``` in the linked github for an example. The list of pairwise comparisons refers to the sentence index (starting at 0), wherein the first number is the easier sentence and the second number is the harder sentence.

To run the code:
```
python3 -m tssort comparisons.txt sentences.txt [-l or -n]
```
where the ```comparisons.txt``` file is your list of comparisons and the ```sentences.txt``` file is you list of sentences. Note, the ```comparisons.txt``` file must reference the index ordering of sentences in the ```sentences.txt``` file.

The ```-l``` argument will output the ranked list of the sentences, from easiest to hardest.

The ```-n``` argument outputs suggestions for the sentences that should be compared next to ensure the most efficient method of sorting the list. 

