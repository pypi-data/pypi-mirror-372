def fullscreen(text, size, fgcolor, bgcolor):
    import tkinter.messagebox
    def close_window():  # 定义一个close_window函数,用root.destroy()方法关闭Tkinter窗口
        root.destroy()
    root = tkinter.Tk()
    root.title('警报:')
    root.overrideredirect(True)  # 取消最小化,最大化,关闭按钮
    root.protocol('WM_DELETE_WINDOW', close_window)  # 手动添加关闭按钮
    root.attributes('-topmost', True)  # 窗口置顶
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
        #bg=bgcolor  # 确保标签背景与窗口一致
    )
    #label_answer.pack(expand=True)  # 居中显示
    label_answer.pack()
    # 创建一个Button组件close_button,设置其文本为关闭,将其command属性绑定到close_window函数,点击按钮是会关闭窗口
    close_button = tkinter.Button(root, text='关闭', command=close_window,
                                  font=('Arial', 30), fg='blue', bg='#7093db')
    close_button.pack(pady=50)  # 用pack方法将按钮放置在窗口中,pady=20用于设置按钮与上方组件的垂直间距
    root.mainloop()
# 如果直接运行，提供一个示例
if __name__ == "__main__":
    fullscreen("Warning!", 40, "blue", "red")


