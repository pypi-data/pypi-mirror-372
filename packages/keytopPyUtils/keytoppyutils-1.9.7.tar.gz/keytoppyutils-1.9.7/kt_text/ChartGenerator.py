import ast
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
from kt_base import CommonUtils
from kt_text.Config import Config


class ChartGenerator:
    def __init__(self,param):
        """
        初始化图表生成器
        :param param: 参数字典，包含标题、轴标签、数据等配置
        """
        # 标题配置
        self.title_name = param.get("titleName","") or ""
        self.title_color = param.get("titleColor","#EE3B3B") or "#EE3B3B"
        self.title_font_size = param.get("titleFontSize",16) or 16

        # X轴配置
        self.x_label_name = param.get("xLabelName","X轴") or "X轴"
        self.x_label_color = param.get("xLabelColor","#333333") or "#333333"

        # Y轴配置
        self.y_label_name = param.get("yLabelName","Y轴") or "Y轴"
        self.y_label_color = param.get("yLabelColor","#333333") or "#333333"

        # 数据键配置
        self.x_key = param.get("xKey")
        if self.x_key is None:
            raise Exception("X轴取数标识：xKey，不能为空")

        # Y轴数据键解析（字符串转字典）
        self.y_keys = param.get("yKeys")
        if self.y_keys is None:
            raise Exception("Y轴取数标识：yKeys，不能为空")
        self.y_keys = ast.literal_eval("{" + self.y_keys + "}")

        # 原始数据解析
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
        """
        生成折线图
        :return: 返回文件名称
        """
        grouped_data, x = self.build_data()
        fig,ax = self.before_config()
        # 绘制折线
        for key in self.y_keys:
            ax.plot(x, grouped_data[key], label=key, color=self.y_keys[key], marker='o', linestyle='-')

        # 1. 明确设置刻度位置（索引或原始值）
        ax.set_xticks(range(len(x)))  # 假设 x 是分类数据（如字符串列表）
        # 或 ax.set_xticks(x)        # 如果 x 是数值型数据

        # 2. 设置标签属性（旋转、对齐、字体）
        ax.set_xticklabels(
            x,  # 标签内容
            rotation=45,
            va='top',
            ha='right',
            rotation_mode='anchor',  # 以锚点为中心旋转
            fontsize=10
        )

        ax.tick_params(axis='y', labelsize=12)

        # 调整底部边距避免标签被裁剪（原0.2可能不足）
        plt.subplots_adjust(bottom=0.25)  # 根据实际效果调整数值

        self.legend_config(ax)
        filename = self.save_img()
        plt.close(fig)
        return filename


    def generate_bar_chart(self):
        """
        生成柱状图
        :return: 返回文件名称
        """
        grouped_data, x = self.build_data()
        fig,ax = self.before_config()
        bar_width = 0.2
        min_bar_width = 0.05
        team_size = len(grouped_data)
        if team_size > 2:
            bar_width = bar_width - (team_size - 2) * 0.02
        if bar_width < min_bar_width:
            bar_width = min_bar_width
        index = range(len(x))

        def draw_bars(ax, index, sales_data, width):
            bars = []
            for i, (team, sales) in enumerate(sales_data.items()):
                offset = width * i - (width * (len(sales_data) - 1)) / 2
                bars.append(ax.bar([x + offset for x in index], sales, width, color=self.y_keys[team], label=team, zorder=2))
            return bars

        bars = draw_bars(ax, index, grouped_data, bar_width)
        ax.set_xticks([i for i in index])
        ax.set_xticklabels(x)

        self.legend_config(ax)

        def add_labels(bars):
            for bar_set in bars:
                for rect in bar_set:
                    height = rect.get_height()
                    ax.annotate('{}'.format(height),
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

        add_labels(bars)
        filename = self.save_img()
        plt.close(fig)
        return filename


    def legend_config(self, ax):
        ax.legend(loc='lower center', bbox_to_anchor=(0.5,-0.35), ncol=8,
                  frameon=False, handlelength=1, handletextpad=0.6, fontsize=10)
        ax.tick_params(colors='#333333')
        ax.grid(True, linestyle='--', color='#D3D3D3', zorder=1)

    def save_img(self):
        file_name = CommonUtils.generate_uuid() + ".png";
        plt.savefig(Config.BASE_PATH + file_name)
        return file_name

    def before_config(self):
        plt.rcParams['font.sans-serif'] = ['SimSun']
        plt.rcParams['axes.unicode_minus'] = False
        fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        fig.subplots_adjust(left=0.1)
        fig.subplots_adjust(bottom=0.15)
        ax.set_facecolor('#FFFFFF')
        for spine in ax.spines.values():
            spine.set_color('#d7d7d7')
        #
        ax.set_title(self.title_name, color=self.title_color, fontsize=self.title_font_size, fontweight='bold',
                     pad=20)
        ax.set_xlabel(self.x_label_name, color=self.x_label_color, fontsize=12, labelpad=10)
        ax.set_ylabel(self.y_label_name, color=self.y_label_color, fontsize=12, labelpad=10)
        return fig,ax

    def build_data(self):
        x = []
        grouped_data = {key: [] for key in self.y_keys}
        for item in self.data:
            x.append(item.get(self.x_key))
            for key in self.y_keys:
                grouped_data[key].append(item[key])
        return grouped_data, x