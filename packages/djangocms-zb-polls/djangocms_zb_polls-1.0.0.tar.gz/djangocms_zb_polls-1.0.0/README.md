Django CMS Zibanu Organizations
-----------

Django CMS Zibanu Organizations es un complemento para django CMS que le permite agregar información de empresas u 
organizaciones en el admin de DjangoCMS clasificándolas por categorías. La información que puede agregar es: Nombre, 
Dirección, Teléfono, Email, Country, Región, Subregión, Logo, Categorías, Ubicación (Latitud, Longitud), polígonos
mediante archivo .shp y Contactos (Nombre, Teléfono, Email). También se puede crear un Microsite por cada organización 
con su respectiva url, en el cual mostrara un carrusel de imágenes, logo, resumen, contenido y los productos que ofrece 
la organización o empresa y sus datos de contacto.

Cuenta con dos plugins:

El plugin Organizations Manager Plugin for Django CMS, al agregarlo en cualquiera de los placeholder de su plantilla, 
puede elegir una categoría y se mostrará un mapa de OpenStreetMap con un listado de organizaciones ubicados en el 
mapa, al hacer clic sobre el nombre organizaciones se mostrará su información en la columna derecha, se realizará un 
zoom sobre la ubicación y se mostrarán los polígonos si los tiene. Este plugin tiene un filtro para realizar
busquedas por ciudad, categoría, producto y nombre.

El plugin Organizations Logo Carousel Admin Plugin for Django CMS, al agregarlo en cualquiera de los placeholder de su 
plantilla, puede elegir una categoría y se mostrará un carrusel de logos de organizaciones y al hacer clic sobre este
abre el micrositio, si lo tiene.

* Las imágenes son administradas por Django Filer. 
* Los campos de texto se manejan con Django ckeditor
* Los países, regiones y subregiones son administrados por Django Cities Light.
* Los estilos se manejan con bootstrap 4.3.1
* Los iconos se manejan con FontAwesome 6.1.1
* Para agregar el mapa se utiliza la librería de LeafLet con OpenStreetMap.
* Para realizar el procesamiento de los archivos .shp se utiliza la librería Geopandas.
* Para manejar todo el tema de coordenadas y georreferenciación se utiliza GeoDjango con las librerías GDAL y PROJ.


Documentación
-----------

Ver requerimientos en el archivo setup.cfg para dependencias adicionales:

python 3.9+ < 4.0 - django 3.2.11 - django CMS 3.9.0 - django-filer 2.1.2 - django-cities-light 3.9.0+ - 
djangorestframework 3.13.1 - djangorestframework-gis 1.0 - django-ckeditor+ 
para el procesamiento de .shp y visualización de polígonos geopandas 0.11.1 - GDAL 3.4.3


Asegúrese de que las siguientes aplicaciones esten instaladas y configuradas correctamente:
* django-filer - https://django-filer.readthedocs.io/en/latest/installation.html
* django-cities-light - https://django-cities-light.readthedocs.io/en/stable-3.x.x/
* django-ckeditor - https://django-ckeditor.readthedocs.io/en/latest/
* FontAwesome - https://fontawesome.com/
* bootstrap - https://getbootstrap.com/docs/4.3/getting-started/introduction/
* djangorestframework - https://www.django-rest-framework.org/
* djangorestframework-gis - https://github.com/openwisp/django-rest-framework-gis
para el procesamiento de .shp y visualización de polígonos
* geopandas - https://geopandas.org/en/stable/getting_started.html
* Configurar todo lo relacionado con GeoDjango - GDAL - PROJ - https://docs.djangoproject.com/en/4.1/ref/contrib/gis/

Instalación
-----------

1. Correr pip install djangocms-zb-organizations
2. Añadir 'djangocms_zb_organizations' a su INSTALLED_APPS
3. Correr "python manage.py migrate"
4. Incluya en urls.py de su proyecto la URLconf de Django CMS Zibanu Organizations con un nombre antes de cms.urls así:

    
    urlpatterns = [
       path('admin/', admin.site.urls),
       path('djangocms_zb_organizations/', include(('djangocms_zb_organizations.urls', 'organizations'))),
       path('', include('cms.urls')),
    ]

5. Inicie el servidor de desarrollo y visite http://su_servidor/admin/
    para administrar Django CMS Zibanu Organizations  (Necesitará que la aplicación Admin esté habilitada).


Configuración
------
Tenga en cuenta que las plantillas proporcionadas son mínimas por diseño. 
Las puede adaptar y anular según los requisitos de su proyecto.

Este complemento proporciona una plantilla default para todas las instancias. Puede proporcionar opciones de plantilla 
adicionales agregando en settings.py lo siguiente:

    DJANGOCMS_ZB_ORGANIZATIONS_TEMPLATES = [
        ('template_mejorado', _('Template Mejorado')),
    ]

Tendrá que crear la carpeta template_mejorado dentro de templates/djangocms_zb_organizations/ de lo contrario, 
obtendrá un error de plantilla que no existe. Puede hacer esto copiando la carpeta default dentro de ese directorio y 
renombrándola a template_mejorado.

Para que la plantilla de los Microsite cargue correctamente su template del proyecto debe tener un bloque con nombre
content de la siguiente forma: 
* {% block content %}{% endblock content %}.

También puede adaptar la plantilla de los microsite de acuerdo a sus necesidades creando el archivo micro_site.html en
templates/djangocms_zb_organizations/

Puede limitar la cantidad de imágenes que se permiten agregar al momento de crear un microsite, estas son las que se
muestran en el carrusel, por default está configurado para permitir mínimo 1 y máximo 2. Para cambiar los valores se
debe declarar las siguientes constantes en su archivo settings.py.
* DJANGOCMS_ZB_ORGANIZATIONS_SLIDER_MIN = número_mínimo
* DJANGOCMS_ZB_ORGANIZATIONS_SLIDER_MAX = número_máximo

Se puede configurar un mensaje tipo disclaimer para que se muestre en la página de Microsite. Para agregar el mensaje se
debe declarar la siguiente constante en el archivo settings.py
* DJANGOCMS_ZB_ORGANIZATIONS_MS_DISCLAIMER = "Texto_del_mensaje"

Para procesar los archivos .shp y obtener los polígonos el S.O. del servidor debe tener configurado el directorio temp,
de lo contrario puede declarar la siguiente constante en el archivo settings.py:
* DJANGOCMS_ZB_ORGANIZATIONS_TEMP_DIR = "ruta_del_directorio"

Es de aclarar que los archivos se eliminan después de procesados, pero si no está configurado el directorio temporal del
S.O. y tampoco la constante, estos archivos no se procesarán.

Endpoints
---------

Djangocms_zb_organizations cuenta con los siguientes endpoints:

1) /djangocms_zb_organizations/organization/counter/by_category/
* Este endpoint muestra el total de organizaciones filtrando por una categoría, para utilizarlo se debe agregar en el
código html un elemento con un id total_oraganizations y en un archivo .js se debe agregar el siguiente código:

       
    /* Codigo para cargar el counter de organizations */
       const category_id = {category_id: id de la categoría por la cual se quiere filtrar}
       let url = "/djangocms_zb_organizations/organization/counter/by-category/";
       let instance = document.getElementById('total_organizations');
       if (instance)
           fetch(
               url,
               {
                   method: "POST",
                   body: JSON.stringify(category_id),
                   headers: {
                       "X-CSRFToken": $('input[name=csrfmiddlewaretoken]').val(),
                       "Content-type": "application/json; charset=UTF-8",
                   }
               }
           ).then((response) => {
               if (response.ok && response.status === 200)
                   return response.json();
               else {
                   throw Error(response.statusText);
               }
           }).then((data) => {
               instance.innerText = data;
           }).catch((error) => {
               instance.innerText = "0";
           })

2) /djangocms_zb_organizations/organization/by_category/
* Este endpoint obtiene un listado de organizaciones con sus poligonos filtrando por una categoría.