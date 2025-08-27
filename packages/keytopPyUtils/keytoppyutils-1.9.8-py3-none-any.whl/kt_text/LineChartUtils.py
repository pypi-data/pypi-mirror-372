import ast

from kt_base import CommonUtils
from matplotlib import pyplot as plt, ticker
from kt_text.Config import Config

class LineChartUtils:
    def __init__(self,param):
        self.title_name = param.get("titleName")
        if self.title_name is None:
            self.title_name = ""
        self.title_color = param.get("titleColor")
        if self.title_color is None:
            self.title_color = "#EE3B3B"
        self.title_font_size = param.get("titleFontSize")
        if self.title_font_size is None:
            self.title_font_size = 16

        self.x_label_name = param.get("xLabelName")
        if self.x_label_name is None:
            self.x_label_name = ""
        self.x_label_color = param.get("xLabelColor")
        if self.x_label_color is None:
            self.x_label_color = "#333333"

        self.y_label_name = param.get("yLabelName")
        if self.y_label_name is None:
            self.y_label_name = ""
        self.y_label_color = param.get("yLabelColor")
        if self.y_label_color is None:
            self.y_label_color = "#333333"

        self.x_key = param.get("xKey")
        if self.x_key is None:
            raise Exception("X轴取数标识：xKey，不能为空")

        self.y_keys = param.get("yKeys")
        if self.y_keys is None:
            raise Exception("Y轴取数标识：yKeys，不能为空")
        self.y_keys = ast.literal_eval("{" + self.y_keys + "}")

        self.label_left = param.get("label_left")
        if self.label_left is None:
            self.label_left = True
        print(self.label_left)

        self.data = param.get("data")
        if self.data is None:
            raise Exception("用于生成折线图的数据：data，不能为空")
        if isinstance(self.data, str):
            self.data = ast.literal_eval(self.data)

    def __str__(self):
        fields = vars(self)
        field_str = ', '.join([f"{k}={v}" for k, v in fields.items()])
        return f"LineChartUtils({field_str})"

    def generate_line_chart(self):
        x = []
        y_max_len = 0
        grouped_data = {key: [] for key in self.y_keys}
        for item in self.data:
            x.append(item.get(self.x_key))
            for key in self.y_keys:
                y_max_len = y_max_len if y_max_len > len(str(item[key])) else len(str(item[key]))
                grouped_data[key].append(item[key])
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 使用微软雅黑
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        fig_size = (7.5, 4.5)
        if len(self.data) > 10:
            fig_size = (10.5, 4.5)
        fig, ax = plt.subplots(figsize=fig_size, dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        # 解决方案1：禁用科学计数法（保留原始数值）
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=False))
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0f}'))
        # 设置图表内容与画布边缘的边距（单位：画布宽高的比例，范围 0~1）
        """
        plt.subplots_adjust(
            left=0.05,  # 左边距（默认 0.125）
            right=0.95,  # 右边距（默认 0.9）
            bottom=0.1,  # 下边距（默认 0.11）
            top=0.9  # 上边距（默认 0.88）
        )
        """
        ax.set_facecolor('#FFFFFF')
        for spine in ax.spines.values():
            spine.set_color('#d7d7d7')


        for key in self.y_keys:
            ax.plot(x, grouped_data[key], label=key, color=self.y_keys[key], linestyle='-',linewidth=0.8,alpha=0.9)

        if self.title_name != '':
            ax.set_title(self.title_name, color='#333333', fontsize=10, fontweight='bold', pad=20)  # 设置标题颜色
        else:
            plt.subplots_adjust(bottom=0.1,  top=0.9)

        if self.x_label_name != '':
            ax.set_xlabel(self.x_label_name, color='#333333', fontsize=8, labelpad=5)  # 设置X轴标签颜色
            # 调整底部边距防止标签被裁剪
            plt.subplots_adjust(bottom=0.2)
        else:
            plt.subplots_adjust(bottom=0.1, top=0.9)
            # 调整底部边距防止标签被裁剪
            plt.subplots_adjust(bottom=0.15)

        if self.y_label_name != '':
            plt.subplots_adjust(left=0.09, right=0.91)
            ax.set_ylabel(self.y_label_name, color='#333333', fontsize=8, labelpad=6)  # 设置Y轴标签颜色
        else:
            plt.subplots_adjust(left=0.05, right=0.95)

        # 2. 设置标签属性（旋转、对齐、字体）
        ax.set_xticklabels(
            x,  # 标签内容
            rotation=45,
            va='top',
            ha='right',
            rotation_mode='anchor'
        )


        for spine in ['left', 'bottom']:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_color('#d7d7d7')  # 目标颜色
            ax.spines[spine].set_linewidth(0.5)

        for spine in ['right', 'top']:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_color('#d7d7d7')  # 目标颜色
            ax.spines[spine].set_linewidth(0)

        # 刻度设置
        # 2. 调整刻度线及标签样式
        ax.tick_params(
            direction='out',
            length=4,
            width=0,
            color='#d7d7d7',
            pad=0,
            labelcolor='#2F5597'
        )
        ax.tick_params(axis="both", labelsize=8, colors="#111111",labelleft=self.label_left)
        if 12 < len(self.data) < 18:
            ax.tick_params(axis="x", labelsize=7, colors="#111111")
        elif len(self.data) >= 18:
            ax.tick_params(axis="x", labelsize=6, colors="#111111")

        # 自适应Y轴坐标
        if 5 <= y_max_len < 8:
            ax.tick_params(axis="y", labelsize=7, colors="#111111")
        elif y_max_len >= 8:
            ax.tick_params(axis="y", labelsize=6, colors="#111111")

        ax.grid(True, axis='y', linestyle="-", color="#d7d7d7", linewidth=0.3, alpha=0.5)
        # 添加图例（左上角）
        ax.legend(
            loc='upper left',
            bbox_to_anchor=(0.016, 1),
            ncol=10,
            handlelength=0.5,
            handletextpad=0.5,
            frameon=False,
            borderaxespad=-2,
            # ==== 新增参数 ====
            prop={'size': 8},  # 字体大小
            labelcolor='#333333'  # 字体颜色
        )

        # plt.show()
        filename = self.save_img()
        plt.close(fig)
        return filename


    def save_img(self):
        file_name = CommonUtils.generate_uuid() + ".png";
        plt.savefig(Config.BASE_PATH + file_name)
        return file_name
