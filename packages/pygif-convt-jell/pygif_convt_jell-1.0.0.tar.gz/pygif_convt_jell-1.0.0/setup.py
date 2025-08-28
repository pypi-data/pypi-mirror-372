from setuptools import setup, find_packages

setup(
    name             = 'pygif_convt_jell',
    version          = '1.0.0',
    description      = 'Test package for distribution',
    author           = 'Eunki7',
    author_email     = 'outsider7224@gmail.com',
    url              = '',
    download_url     = '',
    install_requires = ['pillow'],  # 필요한 라이브러리 - 배포 라이브러리 설치 시 자동 설치 됨
	include_package_data=True,
	packages=find_packages(),  # setup.py 가 존재하는 폴더에 존재하는 패키지폴더를 찾아라
    keywords         = ['GIFCONVERTER', 'gifconverter'],  # 공유 패키지 검색 키워드
    python_requires  = '>=3',   # 필요 버전 공지
    zip_safe=False,
    classifiers      = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
) 