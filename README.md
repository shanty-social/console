# Homeland social console

The homeland social console is a container meant to be run within docker on your computer or home server. It allows you to expose containers as websites on the Internet. All the typical steps are done for you:

 - SSL certificates are obtained and installed on your behalf. All website traffic is encrypted end-to-end.
 - DNS is handled automatically, you can select a subdomain of your favorite available shared domain such as `you.homeland.social`.
 - Your internet connection is used for traffic, but your IP address is not exposed publicly.

Think of homeland social as a reverse VPN. Instead of allowing you to connect to websites from an IP address other than your own, this system allows others to connect to your web site using an address other than your own.

![overview](/docs/images/overview.png)