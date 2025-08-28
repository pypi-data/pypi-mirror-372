
#ifndef SPHERICART_EXPORT_H
#define SPHERICART_EXPORT_H

#ifdef SPHERICART_STATIC_DEFINE
#  define SPHERICART_EXPORT
#  define SPHERICART_NO_EXPORT
#else
#  ifndef SPHERICART_EXPORT
#    ifdef sphericart_EXPORTS
        /* We are building this library */
#      define SPHERICART_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define SPHERICART_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef SPHERICART_NO_EXPORT
#    define SPHERICART_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef SPHERICART_DEPRECATED
#  define SPHERICART_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef SPHERICART_DEPRECATED_EXPORT
#  define SPHERICART_DEPRECATED_EXPORT SPHERICART_EXPORT SPHERICART_DEPRECATED
#endif

#ifndef SPHERICART_DEPRECATED_NO_EXPORT
#  define SPHERICART_DEPRECATED_NO_EXPORT SPHERICART_NO_EXPORT SPHERICART_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef SPHERICART_NO_DEPRECATED
#    define SPHERICART_NO_DEPRECATED
#  endif
#endif

#endif /* SPHERICART_EXPORT_H */
