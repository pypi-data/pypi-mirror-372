# novosns-sdk

## 介绍
novosns-sdk 仓库主要为了方便在 CLI 环境下使用 Keil 进行编译, 烧录等等。并提供了类似串口读取等工具。

## 安装教程

使用 Python >= 3.7 运行下面命令
```
pip install novo_sdk
```

## 使用说明

1. 环境中注入 uv4.exe 的路径
    ```
    export UV4_PATH=<uv4.exe path>
    ```

2. 调用 commands

    - `novo_sdk build` 用于编译 Keil 工程
    - `novo_sdk flash` 用于烧录 Keil 工程
    - `novo_sdk monitor` 监听串口
    - `novo_sdk clean` 清除编译产物

3. 可选参数

    - `--project_path` 填写示例路径，为空则默认为当前目录

## 构建 PIP 包

1. pip install build

2. python -m build

3. pip install twine

4. twine upload dist/*

## Change Log

### V0.1.0

- 初始版本