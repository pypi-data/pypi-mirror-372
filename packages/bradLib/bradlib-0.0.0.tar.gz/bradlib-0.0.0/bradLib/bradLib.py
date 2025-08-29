
import pandas as pd
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt

class csv2tab():
    
    def __init__(self, file, caption = "", alignment = "", rnd = None):

        "Convert a csv file to latex table"
        
        file = pd.read_csv(file, header=0)
        
        file = self.numFormat(file)
        
        header = ""
        dataStr = ""
        
        if alignment == "":
            for i in file.columns:
                alignment+="c"
        
        for col in file.columns:
            header += col
            if col != file.columns[len(file.columns)-1]:
                header += " & "
        
        for row in file.index:
            for col in file.columns:
                
                value = file.loc[row,col]
                    
                dataStr += str(value)
                
                if (col != file.columns[-1]):
                    dataStr += " & "
                    
            dataStr += r"\\" + "\n"
        
        tableStart = r"""\begin{table}[htb]
\centering""" + r"\caption{" + caption + r"}" + r"""
\begin{tabular}{""" + alignment + r"}" + r"""
\toprule
"""
        
        tableEnd = r"""\bottomrule
\end{tabular}
\label{tab:}
\end{table}"""
        
        print(tableStart + header + "\\\\\n\\midrule\n" + dataStr + tableEnd)
    
    def sfRound(self, x, sf=1):
        """Round to given significant figures"""
        return float('%s' % float('%.1g' % x))
    
    def numFormat(self, data):
    
        newCols = []
        remCols = []
        cols = list(data.columns)
        
        for i in range(len(data.columns)):
            
            if cols[i].find("Error") == -1:
                column = []
                
                if cols[i] == cols[len(cols)-1]:
                    newCols.append(data[cols[i]])
                
                elif cols[i+1].find("Error") != -1:
                    
                    for j in data.index:
                        data.loc[j, cols[i+1]] = self.sfRound(data.loc[j, cols[i+1]])
                    data[cols[i+1]] = data[cols[i+1]].astype(str)
                        
                    for j in data.index:
                        rnd = int(('%.0E' % Decimal(data.loc[j,cols[i+1]]))[-2:])
                        
                        data.loc[j, cols[i]] = round(data.loc[j, cols[i]], rnd)
                        
                        column.append(f"${data.loc[j, cols[i]]}\\pm{data.loc[j, cols[i+1]]}$")
                        
                    newCols.append(column)
                    remCols.append(cols[i+1])
                
                else:
                    newCols.append(data[cols[i]])
                
            else:
                pass
            
        for col in remCols:
            cols.remove(col)
            
        return pd.DataFrame(np.array(newCols).T, columns=cols)

class plotter():
    """
    A generaliseable plotting class
    """
    def __init__(self, title = None, figsize=(8,5)):
        # Creating the figure and axes objects, setting title
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_title(title)
    
    def plot(self, data, xyLabels = [None, None], label=None, legendLoc="best"):
        xData, yData = data
        self.ax.plot(xData, yData, label=label) # Plotting the data as a line
        self.ax.set_xlabel(xyLabels[0])         # Setting the x and y axis labels
        self.ax.set_ylabel(xyLabels[1])
        if label != None:
            self.ax.legend(loc=legendLoc)       # Applying a legend to the plot
        
    def scatter(self, data, xyLabels = [None, None], label=None, legendLoc="best", c=None, s=10, marker = "o"):
        xData, yData = data
        self.ax.scatter(xData, yData, label=label, c=c, s=s, marker=marker)  # Plotting the data as a scatter
        self.ax.set_xlabel(xyLabels[0])             # Setting the x, y axis labels
        self.ax.set_ylabel(xyLabels[1])
        if label != None:
            self.ax.legend(loc=legendLoc)           # Applying a legend to the plot
        
    def scales(self, xScale, yScale):
        self.ax.set_xscale(xScale)
        self.ax.set_yscale(yScale)
        
    def limits(self, xLimitD=None, xLimitU=None, yLimitD=None, yLimitU=None):
        # Setting the x and y axes limits
        self.ax.set_xlim(xLimitD, xLimitU)  
        self.ax.set_ylim(yLimitD, yLimitU)
        
    def grid(self, c="k"):
        # Setting the grid of the plot
        self.ax.grid(which='major', color=c, linestyle='-', linewidth=0.6, alpha = 0.6)
        self.ax.grid(which='minor', color=c, linestyle='--', linewidth=0.4, alpha = 0.4)
        self.ax.minorticks_on()     # Turning on minorticks
        self.ax.set_axisbelow(True) # Setting the axis below the data
        
    def aspect(self, aspectRatio="equal"):
        self.ax.set_aspect(aspectRatio) # Setting the aspect ratio of the axes
    
    def defaultPlot(self, data, xyLabels, label=None):
        # Default parameters for quick line plotting
        self.plot(data, xyLabels, label)
        self.grid()
    
    def defaultScatter(self, data, xyLabels, label=None):
        # Default parameters for quick scatter plotting
        self.scatter(data, xyLabels, label)
        self.grid()
    
    def save(self, name):
        self.fig.savefig(name)
        
    def invert(self, axis="both"):
        # Invert the axes
        if axis == "both":
            plt.gca().invert_xaxis()
            plt.gca().invert_yaxis()
        if axis == "x":
            plt.gca().invert_xaxis()
        if axis == "y":
            plt.gca().invert_yaxis()
            
    def imshow(self, data, cmap="gray"):
        # Plot an imshow
        im = self.ax.imshow(data, cmap=cmap)
        self.fig.colorbar(im, ax=self.ax)
        
    def errorbar(self, data, errorbars):
        # Plot errobars
        self.ax.errorbar(data[0], data[1], xerr=errorbars[0], yerr=errorbars[1], fmt="none", capsize=5, elinewidth=2, markeredgewidth=2)
    
    def legend(self):
        self.ax.legend()
