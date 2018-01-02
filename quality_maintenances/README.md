## Usage

```bash
# 安装系统依赖
> yum install python-devel mysql-devel
[...]

# 安装 python 组件依赖（离线情况下使用）
> pip install --no-index --find-links=quality_maintenances_packages/ -r quality_maintenances/requirements.txt 

# 部署
> python setup.py develop
[...]

# 测试
> python tests.py

# 使用说明
> quality_maintenances --help
```
