#!/bin/bash

echo "---------- begin:$0 -----------"

# 按照名称查找进程
PNAME="main.py"
PID_NAME=$(ps -ef | grep -E "$PNAME" | grep -v grep | grep -v "tail" | grep -v "$0" | awk '{ print $2 }')

# 检查PID_NAME是否为空
if [ -z "$PID_NAME" ]; then
    echo "未找到名为 $PNAME 的进程。"
    exit 0
fi

# 将PID_NAME转换为数组，并输出
PID_ARRAY=($PID_NAME)
echo -e "找到以下进程ID：${PID_ARRAY[@]}"

# 按照进程号杀死进程，检查PID合法性，并停止进程
for PID in "${PID_ARRAY[@]}"; do
    # 检查PID是否为有效数字
    if ! [[ "$PID" =~ ^[0-9]+$ ]]; then
        echo "$PID 不是有效的进程ID，跳过。"
        continue
    fi

    # 检查进程是否存在，并停止
    PROC_INFO=$(ps -aux -q "$PID" --no-headers)
    if [ -z "$PROC_INFO" ]; then
        echo "进程 $PID 不存在，跳过。"
        continue
    else
        echo "进程 $PID 信息：$PROC_INFO"
        if [ $? -eq 0 ]; then
            echo "成功停止进程 $PID。"
        else
            echo "无法停止进程 $PID。"
        fi
    fi
done

echo "所有相关进程已处理完成。"

echo -e "---------- end:$0 -----------"