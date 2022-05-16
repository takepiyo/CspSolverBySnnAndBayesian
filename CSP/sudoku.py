import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anm
from IPython.display import display, HTML


class Sudoku:
    def __init__(self, init, answer=None):
        if not isinstance(init, np.ndarray):
            init = np.array(init)
        self.init = init
        self.mask = np.where(init == 0, 1, 0)
        self.previous_answer = None
        self.answer = answer

    def draw(self, spiketrains, spike_processor, sim_time, plot_time_interval, answer=None):

        self.fig, self.ax = plt.subplots(figsize=(4, 4), facecolor="white")
        self.ani = anm.FuncAnimation(
            self.fig,
            self._update,
            fargs=(spiketrains, spike_processor, plot_time_interval),
            frames=range(sim_time + 1),
            init_func=self._init,
            interval=plot_time_interval,
            repeat=False
        )
        display(HTML(self.ani.to_jshtml()))

    def _update(self, i, spiketrains, spike_processor, plot_time_interval):
        self.ax.texts.clear()
        self._draw_num(self.init, "black")
        time_str = "t = %.3f[s]" % (i / 1000)
        self.ax.text(7.5, -1.0, time_str, fontsize=10)
        answer = spike_processor(i, spiketrains)  # read spike at i[ms]
        if answer is None:
            if self.previous_answer is None:
                draw_numbers = self.init
            else:
                draw_numbers = self.previous_answer
        else:
            draw_numbers = self.previous_answer = answer
        draw_numbers *= self.mask  # invalid given number
        self._draw_num(draw_numbers, "salmon")

    def _draw_num(self, num, color):
        for y in range(9):
            for x in range(9):
                v = num[8 - y][x]
                if v > 0:
                    s = str(int(v))
                    self.ax.text(x + 0.5, 8.5 - y, s, va='center',
                                 ha='center', color=color)

    def _init(self):
        self.ax.set_xlim(0, 9)
        self.ax.set_ylim(0, 9)
        self.ax.set_xticks(np.arange(9))
        self.ax.set_yticks(np.arange(9))
        self.ax.tick_params(axis="both", which="both", bottom=False, top=False,
                            labelbottom=False, right=False, left=False, labelleft=False)
        self.ax.grid(linewidth=2)
        self.ax.set_title("Sudoku")
