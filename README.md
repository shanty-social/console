![docker image](https://github.com/homeland-social/console/actions/workflows/docker-image.yml/badge.svg) [![Documentation Status](https://readthedocs.org/projects/homeland-social-console/badge/?version=latest)](https://homeland-social-console.readthedocs.io/en/latest/?badge=latest) ![Docker Pulls](https://img.shields.io/docker/pulls/homelandsocial/console) ![Docker Image Version (latest by date)](https://img.shields.io/docker/v/homelandsocial/console)

# Homeland social console

The homeland social console is a container meant to be run within docker on your computer or home server. It allows you to expose containers as websites on the Internet.

See [full documentation](https://homeland-social-console.readthedocs.io/).

All the typical steps necessary to host a website are done for you:

 - SSL certificates are obtained and installed on your behalf. All website traffic is encrypted end-to-end.
 - DNS is handled automatically, you can select a subdomain of your favorite available shared domain such as `you.homeland.social`.
 - Your internet connection is used for traffic, but your IP address is not exposed publicly.

Think of homeland social as a reverse VPN. Instead of allowing you to connect to websites from an IP address other than your own, this system allows others to connect to your web site using an address other than your own.

![overview](https://raw.githubusercontent.com/homeland-social/console/master/docs/images/overview.png)

# LICENSE

Copyright 2022 Homeland Social

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
