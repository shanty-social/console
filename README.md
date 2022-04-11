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