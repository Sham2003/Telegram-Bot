def intolist(value):
        typing = []
        for val in value:
            if isinstance(val, int):
                val = str(val)
                for i in range(len(val)):
                    typing.append(val[i])
            else:
                for i in range(len(val)):
                    typing.append(val[i])
        return typing


def latextourl(latex_arg):
    url = "https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cfn_cs%20%5Chuge%20"
    latex_list = intolist(latex_arg)
    for j, i in enumerate(latex_list):
        if i == '\\':
            latex_list[j] = '%5C'
        elif i == '{':
            latex_list[j] = '%7B'
        elif i == '}':
            latex_list[j] = '%7D'
        elif i == ' ':
            latex_list[j] = '%20'
        elif i == '+':
            latex_list[j] = '&plus;'
        else:
            pass
    final_latex = "".join(latex_list)
    return str(url + final_latex)
