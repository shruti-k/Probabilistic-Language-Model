import collections
import string
import random
import os,sys

class MarkovChain:

    def __init__(self, prob_file):
        self.prob_file = prob_file
        self.stopwords_list = []
        self.text = ""
        self.unigram_prob  = {}
        self.bigram_prob = {}
        self.trigram_prob = {}
        self.unigrams = []
        self.bigrams = []
        self.trigrams = []
        self.unigram_Counter = {}
        self.bigram_Counter = {}
        self.trigram_Counter = {}

    def read_books(self,dir_path,stopwords_path):
        # listing books from directory
        list_books = os.listdir(dir_path)
        # reading stopwords file
        sw = open(stopwords_path, 'r')
        stopwords = sw.read()
        self.stopwords_list = stopwords.split()

        for book in list_books:
            # reading each book in the author dir
            f = open(dir_path + '\\' + book, 'r')
            booktext = f.read()
            booktext = booktext.lower()

            for p in list(string.punctuation):
                # removing punctuations from text
                booktext = booktext.replace(p, ' ')
            self.text += booktext
        self.text = self.text.lower()

    def calc_unigrams(self):
        # splitting text into unigrams
        unigram_list = self.text.split()
        self.unigrams = [word for word in unigram_list if word.lower() not in self.stopwords_list]
        self.unigram_Counter = collections.Counter(self.unigrams)
        unigram_count = len(self.unigrams)
        self.prob_file.write("-----UNIGRAMS-----\n")
        # calculating prob of each unigram
        for ele in self.unigram_Counter:
            self.unigram_prob[ele] = self.unigram_Counter[ele] / (unigram_count)
            self.prob_file.write("P(" + str(ele) + ") = " + str(self.unigram_Counter[ele] / (unigram_count)))
            self.prob_file.write("\n")

    def calc_bigrams(self):
        # listing bigrams from text
        for words in range(0, len(self.unigrams) - 1):
            ngram = ' '.join(self.unigrams[words:words + 2])
            self.bigrams.append(ngram)
        self.bigram_Counter = collections.Counter(self.bigrams)
        self.prob_file.write("\n\n-----BIGRAMS-----\n")
        for ele in self.bigram_Counter:
            bigram = ele.split()
            if (bigram[0] not in self.bigram_prob):
                self.bigram_prob[bigram[0]] = {}
            self.bigram_prob[bigram[0]][bigram[1]] = (self.bigram_Counter[ele])
        # calculating prob of bigrams
        for par in self.bigram_prob:
            total = sum(list(self.bigram_prob[par].values()))
            for child in self.bigram_prob[par]:
                self.bigram_prob[par][child] /= total
                self.prob_file.write("P(" + str(child) + "|" + str(par) + ") = " + str(self.bigram_prob[par][child]))
                self.prob_file.write("\n")

    def calc_trigrams(self):
        # listing trigrams from text
        for words in range(0, len(self.unigrams) - 2):
            ngram = ' '.join(self.unigrams[words:words + 3])
            self.trigrams.append(ngram)
        self.trigram_Counter = collections.Counter(self.trigrams)
        self.prob_file.write("\n\n-----TRIGRAMS-----\n")
        for ele in self.trigram_Counter:
            trigram = ele.split()
            if (trigram[0] + ' ' + trigram[1] not in self.trigram_prob):
                self.trigram_prob[trigram[0] + ' ' + trigram[1]] = {}
            self.trigram_prob[trigram[0] + ' ' + trigram[1]][trigram[2]] = self.trigram_Counter[ele]
        # calculating prob of trigrams
        for par in self.trigram_prob:
            total = sum(list(self.trigram_prob[par].values()))
            for child in self.trigram_prob[par]:
                self.trigram_prob[par][child] /= total
                self.prob_file.write("P(" + str(child) + "|" + str(par) + ") = " + str(self.trigram_prob[par][child]))
                self.prob_file.write("\n")


    def generate_sentences(self,obj,result_file):
        for s in range(10):
            # choosing unigram, bigrams, trigrams from weighted distribution randomly
            first = random.choices(population=list(self.unigram_prob.keys()), weights=list(self.unigram_prob.values()), k=1)[0]
            sentence = [first]
            prob_model_1 = self.unigram_prob[first]
            prob_model_2 = 1
            if first in self.bigram_prob:
                second_list = self.bigram_prob[first]
                second = random.choices(population=list(list(second_list.keys())), weights=list(list(second_list.values())),k=1)[0]
                sentence.append(second)
                prob_model_1 *= second_list[second]
                for i in range(2, 20):
                    # if no word follows the previous sequence, break from loop
                    if not sentence[i - 2] + ' ' + sentence[i - 1] in self.trigram_prob:
                        break
                    third_list = self.trigram_prob[sentence[i - 2] + ' ' + sentence[i - 1]]
                    third = random.choices(population=list(list(third_list.keys())), weights=list(list(third_list.values())),k=1)[0]
                    sentence.append(third)
                    prob_model_1 *= third_list[third]
            # while evaluating for second model, if word present, multiply by prob value else
            # take prob = 0.01
            if obj.unigram_prob.get(sentence[0]):
                prob_model_2 *= obj.unigram_prob.get(sentence[0])
            else:
                prob_model_2 *= 0.01

            if obj.bigram_prob.get(sentence[0]):
                if obj.bigram_prob[sentence[0]].get(sentence[1]):
                    prob_model_2 *= obj.bigram_prob[sentence[0]].get(sentence[1])
            else:
                prob_model_2 *= 0.01

            for i in range(2,len(sentence)):
                sent = sentence[i - 2] + ' ' + sentence[i - 1]
                if obj.trigram_prob.get(sent):
                    if obj.trigram_prob[sent].get(sentence[i]) :
                        prob_model_2 *= obj.trigram_prob[sent][sentence[i]]
                else:
                    prob_model_2 *= 0.01
            # write sentence and prob from both models to result file
            sent_str = ' '.join(sentence).capitalize()
            result_file.write(str(s + 1) + " : P( " + sent_str + ". ) = " + str(prob_model_1)+" "+str(prob_model_2))
            result_file.write("\n")

if __name__ == "__main__":

    dir_path1 = sys.argv[1]
    dir_path2 = sys.argv[2]
    stopwords_path = sys.argv[3]
    pfile1 = sys.argv[4]
    pfile2 = sys.argv[5]
    rfile = sys.argv[6]

    prob_file1 = open(pfile1, "w")
    prob_file2 = open(pfile2, "w")
    result_file = open(rfile, "w")

    MC1 = MarkovChain(prob_file1)
    MC1.read_books(dir_path1,stopwords_path)
    MC1.calc_unigrams()
    MC1.calc_bigrams()
    MC1.calc_trigrams()

    MC2 = MarkovChain(prob_file2)
    MC2.read_books(dir_path2, stopwords_path)
    MC2.calc_unigrams()
    MC2.calc_bigrams()
    MC2.calc_trigrams()
    result_file.write("Model1:"+dir_path1+"==> Model2:"+dir_path2+"\n")
    MC1.generate_sentences(MC2,result_file)
    result_file.write("\n\n------------------------------------\n\n")
    result_file.write("Model2:"+dir_path2+"==> Model1:"+dir_path1+"\n")
    MC2.generate_sentences(MC1, result_file)


