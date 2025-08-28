def fullscreen(text, size, fgcolor, bgcolor):
    """
    Display a fullscreen alert window.
    
    Args:
        text (str): The text to display
        size (int): Font size
        fgcolor (str): Foreground (text) color
        bgcolor (str): Background color
    """
    import tkinter
    root = tkinter.Tk()
    root.title('警报:')
    root.attributes('-topmost', True)  # 窗口置顶
    root.attributes('-toolwindow', True)  # 工具窗口样式，无最小化按钮
    
    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f'{screen_width}x{screen_height}+0+0')  # 全屏显示
    root.configure(bg=bgcolor)  # 设置背景颜色
    
    # 创建显示文本的标签
    label_answer = tkinter.Label(
        text=f'{text}{screen_width}x{screen_height}',
        font=('Arial', size),
        fg=fgcolor,
        bg=bgcolor  # 确保标签背景与窗口一致
    )
    label_answer.pack(expand=True)  # 居中显示
    root.mainloop()


# 如果直接运行，提供一个示例
if __name__ == "__main__":
    fullscreen("Warning! ", 50, "red", "black")