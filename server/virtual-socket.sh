#!/bin/bash
socat - TCP-LISTEN:3333,fork,reuseaddr
