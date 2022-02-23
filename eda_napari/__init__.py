from napari.utils.notifications import show_info
import matplotlib.pyplot as plt

def show_hello_message():
    show_info('Hello, world!')

def show_plot():
    plt.plot([1, 2, 3, 4])
    plt.ylabel('some numbers')
    plt.show()
