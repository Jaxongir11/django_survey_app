import random
from django.utils.translation import gettext
from django.db.models import Avg
from djf_surveys import models
from djf_surveys.models import TYPE_FIELD, TYPE_FIELD_CHOICES, Survey, Question, Answer, Direction, Question2, Answer2, UserRating, UserAnswer2
from djf_surveys.utils import create_star
import json


COLORS = ['#ff80ed', '#065535', '#133337', '#ffc0cb',
          '#008080', '#ff0000', '#ffd700', '#00ffff',
          '#ffa500', '#0000ff', '#c6e2ff', '#40e0d0',
          '#ff7373', '#666666', '#bada55', '#003366',
          '#fa8072', '#ffb6c1', '#ffff00', '#c0c0c0',
          '#800000', '#800080', '#00ff00', '#7fffd4',
          '#20b2aa', '#f08080', '#cccccc', '#333333',
          '#66cdaa', '#ff00ff', '#ff7f50', '#ff6666',
          '#468499', '#008000', '#00ced1', '#000080',
          '#660066', '#990000', '#f6546a', '#8a2be2',
          '#0e2f44', '#6897bb', '#088da5', '#ccff00',
          '#ff1493', '#ffff66', '#81d8d0', '#ff4040',
          '#2acaea', '#0a75ad', '#420420', '#00ff7f']
# for _ in range(100):
#     # Rangi tasodifiy generatsiya (0..255 intervaldagi 3 kanal).
#     r = random.randint(0, 255)
#     g = random.randint(0, 255)
#     b = random.randint(0, 255)
#     # #RRGGBB formatga aylantirish
#     color_hex = f'#{r:02x}{g:02x}{b:02x}'
#     COLORS.append(color_hex)


class ChartJS:
    """
    this class to generate chart https://www.chartjs.org
    """
    chart_id = ""
    chart_name = ""
    element_html = ""
    element_js = ""
    width = 400
    height = 400
    data = []
    labels = []
    colors = COLORS

    def __init__(self, chart_id: str, chart_name: str, *args, **kwargs):
        self.chart_id = f"djfChart{chart_id}"
        self.chart_name = chart_name

    def _base_element_html(self):
        self.element_html = f"""
<div class="swiper-slide">
    <blockquote class="p-6 border border-gray-100 rounded-lg shadow-lg bg-white">
        <div class="chart-title">
            <h2 style="font-family:arial" class="text-xl font-bold mb-4">{self.chart_name}</h2>
        </div>
        <canvas id="{self.chart_id}" width="{self.width}" height="{self.height}"></canvas>
    </blockquote>
</div>
"""

    def _shake_colors(self):
        self.colors = random.choices(COLORS, k=len(self.labels))

    def _config(self):
        pass

    def _setup(self):
        pass

    def render(self):
        self._base_element_html()
        self._shake_colors()
        script = f"""
{self.element_html}
<script>
{self._setup()}
{self._config()}
  const myChart{self.chart_id} = new Chart(
    document.getElementById('{self.chart_id}'),
    config{self.chart_id}
  );
</script>
"""
        return script


class ChartPie(ChartJS):
    """ this class to generate pie chart"""

    def _config(self):
        script = """
const config%s = {
  type: 'pie',
  data: data%s,
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            family: 'Arial',
            size: 14
          },
          generateLabels: function(chart) {
            const data = chart.data.datasets[0].data;
            const labels = chart.data.labels;
            return labels.map(function(label, index) {
              const value = data[index];
              return {
                text: label + ' (' + value + ')',
                fillStyle: chart.data.datasets[0].backgroundColor[index],
                hidden: false,
                index: index
              };
            });
          }
        }
      },
      tooltip: {
        titleFont: {
          family: 'Arial',
          size: 14
        },
        bodyFont: {
          family: 'Arial',
          size: 14
        }
      },
      title: {
        display: false,
        text: '%s'
      }
    }
  },
};
"""
        return script % (self.chart_id, self.chart_id, self.chart_name)

    def _setup(self):
        script = """
const data%s = {
  labels: %s,
  datasets: [
    {
      label: 'Dataset 1',
      data: %s,
      backgroundColor: %s
    }
  ]
};
"""
        return script % (self.chart_id, self.labels, self.data, self.colors)


class ChartBar(ChartJS):
    """ this class to generate bar chart"""

    def _config(self):
        script = """
const config%s = {
  type: 'bar',
  data: data%s,
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: '%s'
      }
    }
  },
};
"""
        return script % (self.chart_id, self.chart_id, self.chart_name)

    def _setup(self):
        script = """
const data%s = {
  labels: %s,
  datasets: [{
    data: %s,
    backgroundColor: %s,
    borderWidth: 1
  }]
};
"""
        return script % (self.chart_id, self.chart_id, self.chart_name)

    def _setup(self):
        script = """
const data%s = {
  labels: %s,
  datasets: [{
    data: %s,
    backgroundColor: %s,
    borderWidth: 1
  }]
};
"""
        return script % (self.chart_id, self.labels, self.data, self.colors)


class ChartBarRating(ChartBar):
    height = 200
    rate_avg = 0
    num_stars = 5

    def _base_element_html(self):
        stars = create_star(active_star=int(self.rate_avg), num_stars=self.num_stars)
        self.element_html = f"""
<div class="swiper-slide">
    <blockquote class="p-6 border border-gray-100 rounded-lg shadow-lg bg-white">
      <div class="bg-yellow-100 space-y-1 py-5 rounded-md border border-yellow-200 text-center shadow-xs mb-2">
          <h1 class="text-5xl font-semibold"> {self.rate_avg}</h1>
          <div class="flex justify-center">
              {stars}
          </div>
          <h3 class="mb-0 mt-1 text-4xl"> O‘rtacha qiymat</h3>
      </div>
      <canvas id="{self.chart_id}" width="{self.width}" height="{self.height}"></canvas>
    </blockquote>
</div>
"""


class SummaryResponse:

    def __init__(self, survey: Survey, selected_year: int, selected_month: int, selected_direction: Direction):
        self.survey = survey
        self.selected_year = selected_year
        self.selected_month = selected_month
        self.selected_direction = selected_direction

    def get_filtered_queryset(self, queryset):
        # Agar selected_month yoki selected_direction tanlanmagan bo'lsa, ularga filtr qo'llanmaydi.
        if self.selected_year is not None:
            queryset = queryset.filter(created_at__year=self.selected_year)

        if self.selected_month is not None:
            queryset = queryset.filter(created_at__month=self.selected_month)

        if self.selected_direction is not None:
            queryset = queryset.filter(user_answer__direction=self.selected_direction)

        return queryset

    def _process_radio_type(self, question: Question) -> str:
        pie_chart = ChartPie(chart_id=f"chartpie_{question.id}", chart_name=question.label)
        labels = question.choices.split(",")

        data = []
        for label in labels:
            clean_label = label.strip().replace(' ', '_').lower()
            queryset = Answer.objects.filter(question=question, value=clean_label)
            queryset = self.get_filtered_queryset(queryset)
            count = queryset.count()
            data.append(count)

        pie_chart.labels = labels
        pie_chart.data = data
        return pie_chart.render()

    def _process_rating_type(self, question: Question) -> str:
        if not question.choices:  # use 5 as default for backward compatibility
            question.choices = 5

        bar_chart = ChartBarRating(chart_id=f"chartbar_{question.id}", chart_name=question.label)
        bar_chart.num_stars = int(question.choices)
        labels = [str(item + 1) for item in range(int(question.choices))]

        data = []
        for label in labels:
            queryset = Answer.objects.filter(question=question, value=label)
            queryset = self.get_filtered_queryset(queryset)  # Filtrni qo'llash
            count = queryset.count()
            data.append(count)
        queryset = Answer.objects.filter(question=question)
        queryset = self.get_filtered_queryset(queryset)  # Filtrni qo'llash
        values_rating = queryset.values_list('value', flat=True)

        values_convert = [int(v) for v in values_rating]
        try:
            rating_avg = round(sum(values_convert) / len(values_convert), 1)
        except ZeroDivisionError:
            rating_avg = 0
        bar_chart.labels = labels
        bar_chart.data = data
        bar_chart.rate_avg = rating_avg
        return bar_chart.render()

    def _process_multiselect_type(self, question: Question) -> str:
        bar_chart = ChartBar(chart_id=f"barchart_{question.id}", chart_name=question.label)
        labels = question.choices.split(",")

        queryset = Answer.objects.filter(question=question)
        queryset = self.get_filtered_queryset(queryset)  # Filtrni qo'llash
        str_value = [answer.value for answer in queryset]

        all_value = ",".join(str_value)
        data_value = all_value.split(",")

        data = []
        for label in labels:
            clean_label = label.strip().replace(' ', '_').lower()
            data.append(data_value.count(clean_label))

        bar_chart.labels = labels
        bar_chart.data = data
        return bar_chart.render()

    def get_filtered_userrating(self, question2: Question2):
        qs = UserRating.objects.filter(
            user_answer__survey=self.survey
        )
        if self.selected_year is not None:
            qs = qs.filter(user_answer__created_at__year=self.selected_year)
        if self.selected_month is not None:
            qs = qs.filter(user_answer__created_at__month=self.selected_month)
        if self.selected_direction is not None:
            qs = qs.filter(user_answer__direction=self.selected_direction)

        # Shundan so‘ng question2 bo‘yicha ham cheklash
        qs = qs.filter(answer2__question=question2)
        return qs

    def _process_question2_rating_apex(self, question2: Question2):
        qs = self.get_filtered_userrating(question2)

        # 2) rated_users ni o‘ziga quramiz:
        rated_users = (
            qs.values("rated_user__first_name", "rated_user__last_name")
                .annotate(avg_rating=Avg("answer2__value"))
                .order_by("-avg_rating")
        )

        n_users = len(rated_users)  # baholangan userlar soni
        if n_users <= 5:
            column_width = "40%"
        elif n_users <= 10:
            column_width = "20%"
        elif n_users <= 20:
            column_width = "15%"
        elif n_users <= 40:
            column_width = "10%"
        elif n_users <= 80:
            column_width = "5%"
        else:
            column_width = "3%"

        categories = []
        data_series = []

        for user in rated_users:
            first_name = user["rated_user__first_name"] or ""
            last_name = user["rated_user__last_name"] or ""
            full_name = f"{last_name} {first_name}".strip()
            avg_rating = user["avg_rating"] or 0

            categories.append(full_name)
            data_series.append(round(avg_rating, 1))

        # rang massivni JavaScript formatga keltirish

        snippet = f"""
    <div class="mt-8">
      <h2 class="text-xl font-bold mb-4">{question2.label}</h2>
      <div id="apexchart_q2_{question2.id}" style="height: 400px;"></div>
    </div>
    <script>
    var options_q2_{question2.id} = {{
      series: [{{
        data: {data_series}
      }}],
      chart: {{
        type: 'bar',
        height: 400,
        fontFamily: 'Arial, sans-serif',
      }},
      colors: ['#003366'],
      plotOptions: {{
        bar: {{
          columnWidth: '{column_width}',
          dataLabels: {{
            position: 'top'
          }}
        }}
      }},
      dataLabels: {{
        enabled: true,
        offsetY: -20,        // ustun tepasidan -20px balandda chiqsin
        style: {{
          colors: ['#000'],  // qora rang
          fontSize: '12px',
        }}
      }},
      xaxis: {{
        categories: {categories},
        labels: {{
            rotate: -45,
            rotateAlways: true,
            style: {{ fontSize: '14px'}}
        }}
      }}
    }};

    var chart_q2_{question2.id} = new ApexCharts(
      document.querySelector("#apexchart_q2_{question2.id}"),
      options_q2_{question2.id}
    );
    chart_q2_{question2.id}.render();
    </script>
    """
        return snippet

    def _process_question2_aggregate_rating_apex(self) -> str:
        """
        Barcha Question2 savollariga berilgan javoblarni umumlashtirib, foydalanuvchilarni o'rtacha reytinglari bilan ApexCharts bar chartini yaratadi.
        """

        qs = UserRating.objects.filter(user_answer__survey=self.survey)

        # Filtrlarni qo'llash
        if self.selected_year is not None:
            qs = qs.filter(user_answer__created_at__year=self.selected_year)
        if self.selected_month is not None:
            qs = qs.filter(user_answer__created_at__month=self.selected_month)
        if self.selected_direction is not None:
            qs = qs.filter(user_answer__direction=self.selected_direction)

        # Har bir foydalanuvchi uchun o'rtacha reytingni hisoblash
        aggregated_ratings = (
            qs.values("rated_user__first_name", "rated_user__last_name")
                .annotate(avg_rating=Avg("answer2__value"))
                .order_by("-avg_rating")
        )

        n_users = len(aggregated_ratings)  # baholangan userlar soni
        if n_users <= 5:
            column_width = "40%"
        elif n_users <= 10:
            column_width = "20%"
        elif n_users <= 20:
            column_width = "15%"
        elif n_users <= 40:
            column_width = "10%"
        elif n_users <= 80:
            column_width = "5%"
        else:
            column_width = "3%"

        # Agar hech qanday reyting bo'lmasa, grafikni ko'rsatmaymiz
        if not aggregated_ratings:
            return ""

        categories = []
        data_series = []

        for user in aggregated_ratings:
            first_name = user["rated_user__first_name"] or ""
            last_name = user["rated_user__last_name"] or ""
            full_name = f"{last_name} {first_name}".strip()
            avg_rating = user["avg_rating"] or 0

            categories.append(full_name)
            data_series.append(round(avg_rating, 1))

        # Ranglar ro'yxatini tayyorlash
        colors = ['#4CAF50'] * len(categories)  # Yashil rang, kerakli rangni o'zgartiring

        # JSON formatga o'tkazish
        categories_json = json.dumps(categories)
        data_series_json = json.dumps(data_series)
        colors_json = json.dumps(colors)

        # ApexChart konfiguratsiyasi
        snippet = f"""
        <div class="mt-8">
          <h2 class="text-xl font-bold mb-4">Professor-o'qituvchilarning umumiy reytingi</h2>
          <div id="apexchart_aggregate_rating" style="height: 400px;"></div>
        </div>
        <script>
        var options_aggregate_rating = {{
          series: [{{
            name: 'Ortacha Reyting',
            data: {data_series_json},
          }}],
          chart: {{
            type: 'bar',
            height: 400,
            fontFamily: 'Arial, sans-serif',
          }},
          colors: {colors_json},
          plotOptions: {{
            bar: {{
              horizontal: false,
              columnWidth: '{column_width}',
              endingShape: 'rounded',
              dataLabels: {{
                position: 'top'
                }}
            }}
          }},
          dataLabels: {{
        enabled: true,
        offsetY: -20,        // ustun tepasidan -20px balandda chiqsin
        style: {{
          colors: ['#000'],  // qora rang
          fontSize: '12px',
          fontFamily: 'Arial, sans-serif'
        }}
      }},
          xaxis: {{
            categories: {categories_json},
            labels: {{
                rotate: -45,
                rotateAlways: true,
                style: {{ 
                    fontSize: '14px',
                    fontFamily: 'Arial, sans-serif'
                }}
            }},
          }},
          yaxis: {{
            title: {{
              text: 'Ortacha Reyting'
            }},
            labels: {{
                style: {{
                    fontSize: '14px',
                    fontFamily: 'Arial, sans-serif'
                }}
            }}
          }},
          tooltip: {{
            y: {{
              formatter: function (val) {{
                return val
              }}
            }}
          }},
          title: {{
            text: 'Barcha savollar boyicha',
            align: 'center',
            style: {{
              fontSize: '16px',
              fontFamily: 'Arial, sans-serif'
            }}
          }}
        }};

        var chart_aggregate_rating = new ApexCharts(
          document.querySelector("#apexchart_aggregate_rating"),
          options_aggregate_rating
        );
        chart_aggregate_rating.render();
        </script>
        """
        return snippet

    def generate_questions(self):
        """
        Faqat Question (model) savollarining natijalarini (radio, select, multi, rating)
        qaytaradi, lekin Question2 emas.
        """
        html_str = []

        for question in self.survey.questions.all():
            if question.type_field == TYPE_FIELD.radio or question.type_field == TYPE_FIELD.select:
                html_str.append(self._process_radio_type(question))
            elif question.type_field == TYPE_FIELD.multi_select:
                html_str.append(self._process_multiselect_type(question))
            elif question.type_field == TYPE_FIELD.rating:
                html_str.append(self._process_rating_type(question))

        if not html_str:
            input_types = ', '.join(str(x[1]) for x in TYPE_FIELD if
                                    x[0] in (
                                        models.TYPE_FIELD.radio,
                                        models.TYPE_FIELD.select,
                                        models.TYPE_FIELD.multi_select,
                                        models.TYPE_FIELD.rating
                                    ))
            return f"""
        <div class="bg-yellow-100 space-y-1 py-5 rounded-md border border-yellow-200 text-center shadow-xs mb-2">
            <h1 class="text-2xl font-semibold">{gettext("No summary")}</h1>
            <h5 class="mb-0 mt-1 text-sm p-2">{gettext("Summary is available only for input type: %ss") % input_types}</h5>
        </div>
        """
            # 3) Hamma to‘plangan HTML'ni join qilib qaytarish
        return " ".join(html_str)

    def generate_question2(self):
        """
        Faqat Question2 (model) savollarining natijalarini (reyting) qaytaradi,
        ya'ni har bir question2 uchun ApexCharts.
        """
        html_str = []
        for question2 in self.survey.questions2.all():
            html_str.append(self._process_question2_rating_apex(question2))

        aggregate_chart = self._process_question2_aggregate_rating_apex()
        if aggregate_chart:
            html_str.append(aggregate_chart)

        # 3) Hamma to‘plangan HTML'ni join qilib qaytarish
        return " ".join(html_str)
