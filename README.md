# What is Hermes?

Hermes is an Olympian god in Greek religion and mythology, son of Zeus and the Pleiad Maia. He is quick and cunning, moves freely between the worlds of the mortal and divine, and is the messenger of the gods. 

Hermes is also our team snippets clone. But much cooler. Because it's free. And hipster. The entire messaging interface is over email.

![](http://www.marvunapp.com/Appendix/hermesmr1.jpg)

# How's this thing work?

Hermes sends out a reminder email to all subscribers on a configurable schedule. It's just like team snippets. You respond to the email with your bullet points. Then on Friday morning at 9a Eastern, Hermes sends everyone the summary email. Boom.

To subscribe people on the team, admins (Aaron, Alyssa, Crystal, Dan, Robin) subscribe people over email by sending Hermes a request. For example, to subscribe Craig and Nigel, we send this to Hermes via `admin@hermes-hub.appspotmail.com`:

```
Craig Hansen, chansen@wri.org, subscribe
Nigel Sizer, nsizer@wri.org, subscribe
```

Oops. Nigel needs to be an admin and Craig wants to unsubscribe. No problem:

```
Craig Hansen, chansen@wri.org, unsubscribe
Nigel Sizer, nsizer@wri.org, subscribe, admin
```

Hermes sends back a confirmation email each time with a summary of subscriptions:

```
Your changes were saved:

Craig Hansen, chansen@wri.org, unsubscribe
Nigel Sizer, nsizer@wri.org, subscribe, admin
```

That's it. Pretty simple. 
