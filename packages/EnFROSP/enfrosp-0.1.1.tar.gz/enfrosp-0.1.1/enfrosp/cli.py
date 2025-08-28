#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for enfrosp."""

# EnFROSP, EnMAP Fast Retrieval Of Snow Properties
#
# Copyright (c) 2024–2025, GFZ Helmholtz Centre Potsdam, Daniel Scheffler (danschef@gfz.de)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys


def get_enfrosp_argparser():
    """Get a console argument parser for EnFROSP."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')

    return parser


def main():
    argparser = get_enfrosp_argparser()
    parsed_args = argparser.parse_args()

    print("Arguments: " + str(parsed_args._))
    print("Replace this message by putting your code into "
          "enfrosp.cli")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
