
<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/topher-au/pygobject-templatemeta">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">pygobject-templatemeta</h3>

  <p align="center">
    a simpler, easier way to use templates with PyGObject
    <br />
    <a href="https://github.com/topher-au/pygobject-templatemeta"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/topher-au/pygobject-templatemeta">View Demo</a>
    &middot;
    <a href="https://github.com/topher-au/pygobject-templatemeta/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/topher-au/pygobject-templatemeta/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started. To avoid retyping too much info, do a search and replace with your text editor for the following: `topher-au`, `pygobject-templatemeta`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `pygobject-templatemeta`, ` a simpler, easier way to use templates with PyGObject`, `project_license`

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python.org]][Python-url]
* [![Gnome][Gnome.org]][Gnome-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/topher-au/pygobject-templatemeta.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin topher-au/pygobject-templatemeta
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage




The [```Gtk.Builder```][Gtk.Builder] class can be used to construct UI widgets without
needing to write code. The widgets are defined using XML and then loaded
at runtime using the Builder class, which will construct the objects
automatically.

The XML definition can be written manually, or you can use an application
such as [Cambalache][Cambalache] to design the
widgets in a graphical editor, which can then export the design to an XML
template definition.


### Python code
```python
from gi.repository import Gtk
from pygobject_templatemeta import TemplateMeta

class ExampleWindow(Gtk.Window, metaclass=TemplateMeta,
                    template_path='example_window.ui'):
	__gtype_name__ = 'ExampleWindow'

	example_button: Gtk.Button

	def on_example_button_clicked(self, button: Gtk.Button):
		...
```

### Template code
```xml
<?xml version="1.0" encoding="utf-8">
<interface>
	<template class="ExampleWindow" parent="GtkWindow">
		<child>
			<object class="GtkButton" id="example_button">
				<property name="label">Example Button</property>
				<signal name="click" handler="on_example_button_clicked" />
			</object>
		</child>
	</template>
</interface>
```

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

See the [open issues](https://github.com/topher-au/pygobject-templatemeta/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/topher-au/pygobject-templatemeta/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=topher-au/pygobject-templatemeta" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com

Project Link: [https://github.com/topher-au/pygobject-templatemeta](https://github.com/topher-au/pygobject-templatemeta)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/topher-au/pygobject-templatemeta.svg?style=for-the-badge
[contributors-url]: https://github.com/topher-au/pygobject-templatemeta/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/topher-au/pygobject-templatemeta.svg?style=for-the-badge
[forks-url]: https://github.com/topher-au/pygobject-templatemeta/network/members
[stars-shield]: https://img.shields.io/github/stars/topher-au/pygobject-templatemeta.svg?style=for-the-badge
[stars-url]: https://github.com/topher-au/pygobject-templatemeta/stargazers
[issues-shield]: https://img.shields.io/github/issues/topher-au/pygobject-templatemeta.svg?style=for-the-badge
[issues-url]: https://github.com/topher-au/pygobject-templatemeta/issues
[license-shield]: https://img.shields.io/github/license/topher-au/pygobject-templatemeta.svg?style=for-the-badge
[license-url]: https://github.com/topher-au/pygobject-templatemeta/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/Python-3376AB?style=for-the-badge&logo=python&logoColor=fff
[Python-url]: https://www.python.org/
[Gnome.org]: https://img.shields.io/badge/Gnome-000000?style=for-the-badge&logo=gnome&logoColor=fff
[Gnome-url]: https://pygobject.gnome.org/

[Gtk.Builder]: https://docs.gtk.org/gtk4/class.Builder.html
[Cambalache]: https://gitlab.gnome.org/jpu/cambalache