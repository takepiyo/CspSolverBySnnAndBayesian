import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anm
from IPython.display import display, HTML

puzzles = ([[0, 0, 1,  0, 0, 8,  0, 7, 3],
            [0, 0, 5,  6, 0, 0,  0, 0, 1],
            [7, 0, 0,  0, 0, 1,  0, 0, 0],

            [0, 9, 0,  8, 1, 0,  0, 0, 0],
            [5, 3, 0,  0, 0, 0,  0, 4, 6],
            [0, 0, 0,  0, 6, 5,  0, 3, 0],

            [0, 0, 0,  1, 0, 0,  0, 0, 4],
            [8, 0, 0,  0, 0, 9,  3, 0, 0],
            [9, 4, 0,  5, 0, 0,  7, 0, 0]], [[2, 0, 0,  0, 0, 6,  0, 3, 0],
                                             [4, 8, 0,  0, 1, 9,  0, 0, 0],
                                             [0, 0, 7,  0, 2, 0,  9, 0, 0],

                                             [0, 0, 0,  3, 0, 0,  0, 9, 0],
                                             [7, 0, 8,  0, 0, 0,  1, 0, 5],
                                             [0, 4, 0,  0, 0, 7,  0, 0, 0],

                                             [0, 0, 4,  0, 9, 0,  6, 0, 0],
                                             [0, 0, 0,  6, 4, 0,  0, 1, 9],
                                             [0, 5, 0,  1, 0, 0,  0, 0, 8]], [[0, 0, 3,  2, 0, 0,  0, 7, 0],
                                                                              [0, 0, 5,  0, 0,
                                                                                  0,  3, 0, 0],
                                                                              [0, 0, 8,  9, 7,
                                                                                  0,  0, 5, 0],

                                                                              [0, 0, 0,  8, 9,
                                                                                  0,  0, 0, 0],
                                                                              [0, 5, 0,  0, 0,
                                                                                  0,  0, 2, 0],
                                                                              [0, 0, 0,  0, 6,
                                                                                  1,  0, 0, 0],

                                                                              [0, 1, 0,  0, 2,
                                                                                  5,  6, 0, 0],
                                                                              [0, 0, 4,  0, 0,
                                                                                  0,  8, 0, 0],
                                                                              [0, 9, 0,  0, 0, 7,  5, 0, 0]])


class Sudoku:
    def __init__(self, init):
        if not isinstance(init, np.ndarray):
            init = np.array(init)
        self.init = init
        self.mask = np.where(init == 0, 1, 0)
        self.previous_answer = None

    @classmethod
    def make_sudoku(cls, puzzle=1):
        return Sudoku(puzzles[puzzle])

    # only spike trains
    def draw_sequence(self, spiketrains, spike_processor, sim_time, plot_time_interval, answer=None):

        self.fig, self.ax = plt.subplots(figsize=(4, 4), facecolor="white")
        self.ani = anm.FuncAnimation(
            self.fig,
            self._update,
            fargs=(spiketrains, spike_processor, plot_time_interval),
            frames=range(sim_time + 1),
            init_func=self._init_fig,
            interval=plot_time_interval,
            repeat=False
        )
        display(HTML(self.ani.to_jshtml()))

    def draw(self, answer=None):
        self.fig, self.ax = plt.subplots(figsize=(4, 4), facecolor="white")
        self._init_fig()
        self._draw_num(self.init, "black")
        if answer is not None:
            if not isinstance(answer, np.ndarray):
                answer = np.array(answer)
            answer *= self.mask  # invalid given number
            self._draw_num(answer, "salmon")
        plt.show()

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

    def _init_fig(self):
        self.ax.set_xlim(0, 9)
        self.ax.set_ylim(0, 9)
        self.ax.set_xticks(np.arange(9))
        self.ax.set_yticks(np.arange(9))
        self.ax.tick_params(axis="both", which="both", bottom=False, top=False,
                            labelbottom=False, right=False, left=False, labelleft=False)
        self.ax.grid(linewidth=2)
        self.ax.set_title("Sudoku")

    def solver(self, values, x=0, y=0):
        """
        https://qiita.com/wsldenli/items/78596c8775a0673f255e
        """
        "数独を解く"
        if y > 8:  # ポインタが最後までいったら完成
            return True
        elif values[y][x] != 0:  # 空欄ではないなら飛ばす
            if x == 8:  # 8列までいったら次の行に移動
                if self.solver(values, 0, y+1):
                    return True
            else:
                if self.solver(values, x+1, y):
                    return True
        else:
            for i in range(1, 10):  # 1から9までの数字を全て試す
                if self.check(values, x, y, i):  # チェックする
                    values[y][x] = i  # OKなら数字を入れる
                    if x == 8:  # 8列までいったら次の行に移動
                        if self.solver(values, 0, y+1):
                            return True
                    else:
                        if self.solver(values, x+1, y):
                            return True
            values[y][x] = 0  # 戻ってきたら0に戻す
            return False

    def check(self, values, x, y, i):
        def row(values, y, i):
            "横をチェック"
            return all(True if i != values[y][_x] else False for _x in range(9))

        def column(values, x, i):
            "縦をチェック"
            return all(True if i != values[_y][x] else False for _y in range(9))

        def block(values, x, y, i):
            "3x3のブロックをチェック"
            xbase = (x // 3) * 3
            ybase = (y // 3) * 3
            return all(True if i != values[_y][_x] else False
                       for _y in range(ybase, ybase + 3)
                       for _x in range(xbase, xbase + 3))

        if row(values, y, i) and column(values, x, i) and block(values, x, y, i):
            return True
        return False


if __name__ == "__main__":
    puzzle = 1

    sudoku = Sudoku(init)
    answer = init.copy()
    print(sudoku.solver(answer))
    sudoku.draw(answer)
