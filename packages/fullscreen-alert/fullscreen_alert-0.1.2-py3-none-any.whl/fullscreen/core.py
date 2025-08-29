def fullscreen(text, size=40, fgcolor='blue', bgcolor='red'):
    import tkinter
    import tkinter.messagebox
    def close_window():  # 定义一个close_window函数,用root.destroy()方法关闭Tkinter窗口
        root.destroy()

    root = tkinter.Tk()
    #root.title('警报:')
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
        root,  # 明确指定父窗口
        text=f'{text}\n\n屏幕分辨率:{screen_width}x{screen_height}',
        font=('Arial', size),
        fg=fgcolor,
       # bg=bgcolor,  # 确保标签背景与窗口一致
        justify='center'  # 文本居中
    )
    label_answer.pack(expand=True)  # 居中显示

    # 创建一个Button组件close_button,设置其文本为关闭,将其command属性绑定到close_window函数
    close_button = tkinter.Button(root, text='关闭', command=close_window,
                                  font=('Arial', 30), fg='blue', bg='#7093db')

    # 使用place将按钮放置在右下角
    close_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)  # 距离右下角10像素
    #使用place几何管理器替代pack来定位关闭按钮
    #relx = 1.0, rely = 1.0表示相对于父容器的位置（1.0表示100 %，即右下角）
    #anchor = 'se'表示锚点在东南角（右下角）x = -10, y = -10表示从右下角向左上偏移10像素，留出一些边距

    root.mainloop()

# 如果直接运行，提供一个示例
if __name__ == "__main__":
    fullscreen('\n载具号:FIX-2019012345 位置1不良\n\n是手动指定需要挑出维修的载具，\n已锁定载具，请取出送修\n请先取走载具,'
               '再关闭报警画面!\n\n无论本次有无不良都请取出送修!')