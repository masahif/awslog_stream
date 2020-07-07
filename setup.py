#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

def main():
    setup(
        name='awslog_stream',
        version='1.0.1',
        description="stdin to cloudwatch logs",
        author="Mashiro Fukuda",
        author_email='masahif@hotmail.com',
        url='https://github.com/masahif/awslog_stream',
        packages=['awslog_stream'],
        entry_points={
            'console_scripts': [
                'awslog_stream=awslog_stream.stdin_handler:handler',
            ]
        },
        classifiers=[
           'Programming Language :: Python :: 3.6',
        ]
    )


if __name__ == '__main__':
    main()
