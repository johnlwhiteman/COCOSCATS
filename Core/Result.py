import re

class Result():

    def getTranslatorContentAsJson(content):
        tokens = content.split("\n")
        idx = []
        for section in ["[VOCABULARY]", "[REJECTED]", "[L1]", "[L2]"]:
            idx.append(tokens.index(section))
        L1 = list(filter(None, tokens[idx[2]+1:idx[3]]))[0].strip()
        L2 = list(filter(None, tokens[idx[3]+1:]))[0].strip()
        L1L2 = L1
        vocabulary = []
        wordlist = list(filter(None, tokens[idx[0]+1:idx[1]]))
        for token in wordlist:
            l1, l2, pos, cnt = token.split(",")
            L1L2 = re.sub(r"\b{0}\b".format(l1), "{{{0}}}".format(l2), L1L2, re.IGNORECASE)
            vocabulary.append({"l1": l1, "l2": l2, "pos": pos, "cnt": cnt})
        rejected = list(filter(None, tokens[idx[1]+1:idx[2]]))
        return {
            "vocabulary": vocabulary,
            "wordlist": wordlist,
            "rejected": rejected,
            "l1": L1,
            "l2": L2,
            "l1l2": L1L2
        }

