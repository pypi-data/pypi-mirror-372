# Arquivo utilizado para instalar o pacote diretamente para testes, para saber se as atualizações realizadas estão funcionando corretamente
from setuptools import setup, find_packages

setup(
    name="bciflow",
    version="0.1",
    packages=find_packages(),
    package_dir={'': '.'},  # Indica que os pacotes estão no diretório atual
)